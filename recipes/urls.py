from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
router = DefaultRouter()

app_name = 'recipes'

router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientsViewSet, basename='ingredients')
router.register('tags', views.TagsViewSet, basename='tags')

urlpatterns = [
   path('', include(router.urls)),
]