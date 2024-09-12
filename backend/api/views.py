from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
import base64
import short_url

from api.custom_filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserSubscribeRepresentSerializer,
    UserSubscribeSerializer,
    UserGetSerializer
)
from api.utils import create_model_instance, delete_model_instance
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
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
            {'error': 'Invalid avatar data'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        if user.avatar:
            user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get the authenticated user's profile."""
    serializer = UserGetSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeView(APIView):
    """View for getting the current user's information."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserGetSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data)


class UserSubscribeView(APIView):
    """Create/delete subscription to a user."""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if not subscription.exists():
            return Response(
                {'errors': 'You are not subscribed to this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeShortLinkView(APIView):
    """Generate a short link for a recipe."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            recipe = get_object_or_404(Recipe, pk=pk)
            short_link = short_url.encode(recipe.id)
            base_url = request.build_absolute_uri('/')
            full_short_link = f"{base_url}recipes/{short_link}/"
            return Response(
                {'short-link': full_short_link},
                status=status.HTTP_200_OK
            )
        except Recipe.DoesNotExist:
            return Response(
                {'detail': 'Recipe not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Get a list of all user subscriptions."""
    serializer_class = UserSubscribeRepresentSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(following__user=self.request.user)
        return User.objects.none()


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
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
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
            'This recipe is not in your favorites'
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
            'This recipe is not in your shopping cart'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Send a file with a shopping list."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=ShoppingCart.objects.filter(
                user=request.user
            ).values('recipe')
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))

        shopping_list = ['Shopping List:\n']
        shopping_list.extend(
            f'\n{ingredient["ingredient__name"]} - '
            f'{ingredient["ingredient_amount"]}, '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        )

        response = HttpResponse(
            '\n'.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        return response
