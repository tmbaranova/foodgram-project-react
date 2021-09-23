from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import SubscribeViewSet

router = DefaultRouter()

router.register("ingredients", views.IngredientsViewSet,
                basename="ingredients")
router.register("tags", views.TagsViewSet,)
router.register("recipes", views.RecipeViewSet, basename="recipe")


urlpatterns = [
    path("users/<int:author_id>/subscribe/",
         SubscribeViewSet.as_view({"get": "create", "delete": "destroy"}),
         name="subscribe"),
    path("users/subscriptions/", SubscribeViewSet.as_view({"get": "list"}),
         name="subscriptions"),
    path("recipes/<int:recipe_id>/favorite/",
         views.FavoriteViewSet.as_view(
             {"get": "create", "delete": "destroy"}),
         name="favorite"),
    path("recipes/<int:recipe_id>/shopping_cart/",
         views.ShoppingCartViewSet.as_view(
             {"get": "create", "delete": "destroy"}),
         name="shopping_cart"),
    path("recipes/download_shopping_cart/",
         views.download_shopping_cart, name="download"),
    path("", include(router.urls)),
]
