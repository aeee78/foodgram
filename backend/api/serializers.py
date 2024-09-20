"""Serializers for the API application."""

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.constants import MAX_INGREDIENT_AMOUNT, MIN_INGREDIENT_AMOUNT
from api.fields import Base64ImageField
from api.utils import create_ingredients
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserSignUpSerializer(UserCreateSerializer):
    """Serializer for user registration."""

    class Meta:
        """Meta class for UserSignUpSerializer."""

        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class UserGetSerializer(UserSerializer):
    """Serializer for retrieving user information."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        """Meta class for UserGetSerializer."""

        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields

    def to_representation(self, instance):
        """Convert instance to representation."""
        ret = super().to_representation(instance)
        if isinstance(instance, User):
            ret['is_subscribed'] = self.get_is_subscribed(instance)
            ret['avatar'] = self.get_avatar(instance)
        return ret

    def get_is_subscribed(self, obj):
        """Get subscription status."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.follower.filter(author=obj).exists()
        )

    def get_avatar(self, obj):
        """Get avatar URL."""
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return ""


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Serializer for brief recipe information."""

    class Meta:
        """Meta class for RecipeSmallSerializer."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeRepresentSerializer(UserGetSerializer):
    """Serializer for user subscription information."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserGetSerializer.Meta):
        """Meta class for UserSubscribeRepresentSerializer."""

        fields = UserGetSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = fields

    def get_recipes(self, obj):
        """Get recipes for the user."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get(
            'recipes_limit') if request else None
        recipes = obj.recipes.all()

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except (ValueError, TypeError):
                pass

        return RecipeSmallSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        """Get the count of user's recipes."""
        return obj.recipes.count()


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions."""

    class Meta:
        """Meta class for UserSubscribeSerializer."""

        model = Subscription
        fields = ('author', 'user')

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя!'
            )
        ]

    def validate(self, data):
        """Validate subscription data."""
        if data['user'] == data['author']:
            raise ValidationError("Вы не можете подписаться на себя!")
        return data

    def to_representation(self, instance):
        """Convert instance to representation."""
        return UserSubscribeRepresentSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        """Meta class for TagSerializer."""

        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        """Meta class for IngredientSerializer."""

        model = Ingredient
        fields = '__all__'


class IngredientGetSerializer(serializers.ModelSerializer):
    """Serializer for retrieving ingredient information in recipes."""

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        """Meta class for IngredientGetSerializer."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(serializers.ModelSerializer):
    """Serializer for adding ingredients to recipes."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT
    )

    class Meta:
        """Meta class for IngredientPostSerializer."""

        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """Validate the amount field."""
        if value < MIN_INGREDIENT_AMOUNT:
            raise ValidationError(
                f'Количество должно быть не менее {MIN_INGREDIENT_AMOUNT}.'
            )
        if value > MAX_INGREDIENT_AMOUNT:
            raise ValidationError(
                f'Количество должно быть не более {MAX_INGREDIENT_AMOUNT}.'
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    """Serializer for retrieving recipe information."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientGetSerializer(
        many=True, read_only=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        """Meta class for RecipeGetSerializer."""

        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Check if the recipe is favorited by the user."""
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Check if the recipe is in the user's shopping cart."""
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.user_shopping_carts.filter(recipe=obj).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes."""

    ingredients = IngredientPostSerializer(
        many=True, required=True, source='recipeingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    image = Base64ImageField()

    class Meta:
        """Meta class for RecipeCreateSerializer."""

        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, data):
        """Validate recipe data."""
        self._validate_ingredients(data)
        self._validate_tags(data)
        return data

    def _validate_ingredients(self, data):
        """Validate ingredient data."""
        ingredients = data.get('recipeingredients')
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Это поле обязательно.'})

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise ValidationError('Повторяющиеся ингредиенты запрещены.')

    def _validate_tags(self, data):
        """Validate tag data."""
        tags = data.get('tags')
        if not tags:
            raise ValidationError({'tags': 'Это поле обязательно.'})

        tag_ids = set(tag.id for tag in tags)
        if len(tag_ids) != len(tags):
            raise ValidationError('Повторяющиеся теги запрещены.')

    def create(self, validated_data):
        """Create a new recipe."""
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update an existing recipe."""
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()

        create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Convert instance to representation."""
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorite recipes."""

    class Meta:
        """Meta class for FavoriteSerializer."""

        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        """Convert instance to representation."""
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""

    class Meta:
        """Meta class for ShoppingCartSerializer."""

        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в корзину'
            )
        ]

    def to_representation(self, instance):
        """Convert instance to representation."""
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
