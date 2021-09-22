from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


from users.serializers import CustomUserSerializer
from .models import (Amount, Favorite, Ingredient, Recipe, ShoppingCart,
                     Subscribe, Tag)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Amount
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """Get list of recipes or one recipe."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart",
                  "name", "image", "text", "cooking_time")

    def get_ingredients(self, obj):
        queryset = Amount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(instance=queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        recipe = obj
        is_favorited = Favorite.objects.filter(
            user_id=user.id, recipe_id=recipe.id).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        recipe = obj
        is_in_shopping_cart = ShoppingCart.objects.filter(
            user_id=user.id, recipe_id=recipe.id).exists()
        return is_in_shopping_cart


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient", write_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")
    name = serializers.ReadOnlyField(source="ingredient.name")
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ("id", "name", "measurement_unit", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        error_messages={
            "invalid": "Время приготовления не может быть меньше 1 минуты."
        }
    )

    class Meta:
        model = Recipe
        fields = ("ingredients", "tags", "name", "image",
                  "text", "cooking_time")

    def validate_cooking_time(self, data):
        if data < 1:
            raise serializers.ValidationError(
                "Время приготовления не может быть меньше 1 минуты."
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = set(validated_data.pop("tags"))
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients:
            if item["amount"] < 1:
                raise serializers.ValidationError(
                    "Количество ингредиента не может быть меньше 1.")

            ingredient = get_object_or_404(Ingredient, pk=item["ingredient"])
            Amount.objects.create(
                recipe=recipe, ingredient=ingredient, amount=item["amount"])

        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = set(validated_data.pop("tags"))

        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time)
        instance.ingredients.clear()
        instance.save()

        for item in ingredients_data:
            if item["amount"] < 1:
                raise serializers.ValidationError(
                    "Количество ингредиента не может быть меньше 1.")

            ingredient = get_object_or_404(Ingredient, pk=item["ingredient"])
            Amount.objects.create(
                recipe=instance, ingredient=ingredient, amount=item["amount"])

        instance.tags.set(tags_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False, source="author.email")
    id = serializers.IntegerField(required=False, source="author.id")
    username = serializers.CharField(required=False, source="author.username")
    first_name = serializers.CharField(
        required=False, source="author.first_name")
    last_name = serializers.CharField(
        required=False, source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ("email", "id", "username", "first_name",
                  "last_name", "is_subscribed", "recipes", "recipes_count")

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        author = obj.author
        is_subscribed = Subscribe.objects.filter(
            user_id=user.id, author_id=author.id).exists()
        return is_subscribed

    def get_recipes(self, obj):
        queryset = obj.author.author_recipes.all()
        page_size = self.context["request"].query_params.get(
            "recipes_limit") or 6
        paginator = Paginator(queryset, page_size)
        recipes = paginator.page(1)
        serializer = RecipeShortSerializer(recipes, many=True,)
        return serializer.data

    def get_recipes_count(self, obj):
        author = obj.author
        recipes_count = author.author_recipes.count()
        return recipes_count

    def validate(self, data):
        user = self.context["request"].user
        author_id = self.context.get("view").kwargs.get("author_id")

        if user.id == author_id:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя.")
        if Subscribe.objects.filter(user=user.id, author=author_id).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя.")
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, source="recipe.id")
    name = serializers.CharField(required=False, source="recipe.name")
    image = serializers.ImageField(required=False, source="recipe.image")
    cooking_time = serializers.IntegerField(
        required=False, source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        user = self.context["request"].user
        recipe_id = self.context.get("view").kwargs.get("recipe_id")

        if Favorite.objects.filter(user=user.id, recipe=recipe_id).exists():
            raise serializers.ValidationError(
                "Этот рецепт уже в избранном.")
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, source="recipe.id")
    name = serializers.CharField(required=False, source="recipe.name")
    image = serializers.ImageField(required=False, source="recipe.image")
    cooking_time = serializers.IntegerField(
        required=False, source="recipe.cooking_time")

    class Meta:
        model = ShoppingCart
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        user = self.context["request"].user
        recipe_id = self.context.get("view").kwargs.get("recipe_id")

        if ShoppingCart.objects.filter(
                user=user.id, recipe=recipe_id).exists():
            raise serializers.ValidationError(
                "Этот рецепт уже в списке покупок.")
        return data
