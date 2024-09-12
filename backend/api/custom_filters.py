"""Custom filters for Recipe and Ingredient models."""

from django.db.models import Exists, OuterRef
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, ShoppingCart, Tag


class RecipeFilter(FilterSet):
    """
    Custom filter for Recipe model.

    Allows filtering by tags, favorited status, and shopping cart status.
    """

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        """Meta class for RecipeFilter."""

        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Filter queryset by favorited status."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Filter queryset by shopping cart status."""
        user = self.request.user
        if not user.is_authenticated:
            return queryset

        shopping_cart_filter = Exists(
            ShoppingCart.objects.filter(
                user=user,
                recipe=OuterRef('pk')
            )
        )

        if value:
            return queryset.filter(shopping_cart_filter)
        return queryset.exclude(shopping_cart_filter)


class IngredientFilter(FilterSet):
    """
    Custom filter for Ingredient model.

    Allows case-insensitive filtering by name.
    """

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        """Meta class for IngredientFilter."""

        model = Ingredient
        fields = ('name',)
