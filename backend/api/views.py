"""Views for the API application."""

import base64

import short_url
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             ShoppingCartSerializer, TagSerializer,
                             UserGetSerializer,
                             UserSubscribeRepresentSerializer,
                             UserSubscribeSerializer)
from api.utils import create_model_instance, delete_model_instance
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_avatar(request):
    """Update or delete the user's avatar."""
    user = request.user

    if request.method == 'PUT':
        avatar_data = request.data.get('avatar')
        if avatar_data and avatar_data.startswith('data:image'):
            format_data, imgstr = avatar_data.split(';base64,')
            ext = format_data.split('/')[-1]
            avatar = ContentFile(
                base64.b64decode(imgstr),
                name=f'{user.username}_avatar.{ext}'
            )
            user.avatar = avatar
            user.save()
            return JsonResponse(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )
        return JsonResponse(
            {'error': 'Неправильная ссылка на изображение'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.avatar:
        user.avatar.delete()
    user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


class UserMeView(APIView):
    """View for getting the current user's information."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET request to retrieve user information."""
        serializer = UserGetSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data)


class UserSubscribeView(APIView):
    """Create/delete subscription to a user."""

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """Handle POST request to create a subscription."""
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        """Handle DELETE request to remove a subscription."""
        author = get_object_or_404(User, id=user_id)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeShortLinkView(APIView):
    """Generate a short link for a recipe."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Handle GET request to generate a short link."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = short_url.encode(recipe.id)
        base_url = request.build_absolute_uri('/')
        full_short_link = f"{base_url}recipes/{short_link}/"
        return Response(
            {'short-link': full_short_link},
            status=status.HTTP_200_OK
        )


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Get a list of all user subscriptions."""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserSubscribeRepresentSerializer

    def get_queryset(self):
        """Get the queryset for user subscriptions."""
        return User.objects.filter(following__user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Get information about tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Get information about ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for working with recipes."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Get the appropriate serializer class."""
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Add/remove recipe to/from favorites."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)
        return delete_model_instance(
            request,
            Favorite,
            recipe,
            'Этот рецепт не добавлен в избранное'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Add/remove recipe to/from shopping cart."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(
                request,
                recipe,
                ShoppingCartSerializer
            )
        return delete_model_instance(
            request,
            ShoppingCart,
            recipe,
            'Этот рецепт не добавлен в корзину'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def get_shopping_cart_ingredients(self, user):
        """Get aggregated ingredients for user's shopping cart."""
        return RecipeIngredient.objects.filter(
            recipe__in=ShoppingCart.objects.filter(user=user).values('recipe')
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))

    def format_shopping_list(self, ingredients):
        """Format the shopping list as a string."""
        shopping_list = ['Shopping List:\n']
        shopping_list.extend(
            f'\n{ingredient["ingredient__name"]} - '
            f'{ingredient["ingredient_amount"]}, '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        )
        return '\n'.join(shopping_list)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Send a file with a shopping list."""
        ingredients = self.get_shopping_cart_ingredients(request.user)
        shopping_list = self.format_shopping_list(ingredients)

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        return response
