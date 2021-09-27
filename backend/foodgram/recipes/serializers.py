from django.core.paginator import Paginator
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import (Amount, Favorite, Ingredient, Recipe, ShoppingCart,
                     Subscribe, Tag)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        queryset = Amount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(instance=queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        recipe = obj
        is_favorited = Favorite.objects.filter(
            user_id=user.id, recipe_id=recipe.id).exists()
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        recipe = obj
        is_in_shopping_cart = ShoppingCart.objects.filter(
            user_id=user.id, recipe_id=recipe.id).exists()
        return is_in_shopping_cart


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient', write_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        error_messages={
            'invalid': 'Время приготовления не может быть меньше 1 минуты.'
        }
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'image',
                  'text', 'cooking_time')

    def validate_cooking_time(self, data):
        if data < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше минуты.'
            )
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент')
        for ingredient in ingredients:
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1.')

            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент в списке должен быть уникальным.'
                )
            ingredients_set.add(ingredient_id)

        return data

    def add_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if (Amount.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists()):
                amount += F('amount')
            Amount.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount})

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_recipe_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        recipe.image = validated_data.get('image', recipe.image)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.add_recipe_ingredients(ingredients, recipe)
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False, source='author.email')
    id = serializers.IntegerField(required=False, source='author.id')
    username = serializers.CharField(required=False, source='author.username')
    first_name = serializers.CharField(
        required=False, source='author.first_name')
    last_name = serializers.CharField(
        required=False, source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        author = obj.author
        is_subscribed = Subscribe.objects.filter(
            user_id=user.id, author_id=author.id).exists()
        return is_subscribed

    def get_recipes(self, obj):
        queryset = obj.author.recipes.all()
        page_size = self.context['request'].query_params.get(
            'recipes_limit', 6)
        paginator = Paginator(queryset, page_size)
        serializer = RecipeShortSerializer(paginator, many=True,)
        return serializer.data

    def get_recipes_count(self, obj):
        author = obj.author
        recipes_count = author.recipes.count()
        return recipes_count

    def validate(self, data):
        user = self.context['request'].user
        author_id = self.context.get('view').kwargs.get('author_id')

        if user.id == author_id:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        if Subscribe.objects.filter(user=user.id, author=author_id).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, source='recipe.id')
    name = serializers.CharField(required=False, source='recipe.name')
    image = serializers.ImageField(required=False, source='recipe.image')
    cooking_time = serializers.IntegerField(
        required=False, source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context.get('view').kwargs.get('recipe_id')

        if Favorite.objects.filter(user=user.id, recipe=recipe_id).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в избранном.')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, source='recipe.id')
    name = serializers.CharField(required=False, source='recipe.name')
    image = serializers.ImageField(required=False, source='recipe.image')
    cooking_time = serializers.IntegerField(
        required=False, source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context.get('view').kwargs.get('recipe_id')

        if ShoppingCart.objects.filter(
                user=user.id, recipe=recipe_id).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже в списке покупок.')
        return data
