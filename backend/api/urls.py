"""URL configuration for the API endpoints."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, RecipeShortLinkView, RecipeViewSet,
                       TagViewSet, UserMeView, UserSubscribeView,
                       UserSubscriptionsViewSet, update_avatar)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/me/avatar/', update_avatar),
    path('users/subscriptions/',
         UserSubscriptionsViewSet.as_view({'get': 'list'})),
    path('users/<int:user_id>/subscribe/', UserSubscribeView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:pk>/get-link/', RecipeShortLinkView.as_view(),
         name='get_recipe_short_link'),
]
