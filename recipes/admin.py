from django.contrib import admin

from .models import Tag, Recipe, Ingredient, Amount


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "hex_style")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'image', 'description', 'cook_time', 'pub_date')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "unit")


@admin.register(Amount)
class AmountAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "units")
