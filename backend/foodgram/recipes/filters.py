import django_filters

from .models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = django_filters.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite_recipe__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(in_shopping_cart__user=user)
        return Recipe.objects.all()

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'in_shopping_cart', 'author', 'tags', ]
