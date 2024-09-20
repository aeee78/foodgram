"""Filters for Recipe and Ingredient models."""

from django.db.models import Exists, OuterRef
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, ShoppingCart


class RecipeFilter(FilterSet):
    """Filter for Recipe model."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
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
            return queryset.filter(favorites__user=user)
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
        return queryset(shopping_cart_filter)


class IngredientFilter(FilterSet):
    """Filter for Ingredient model."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        """Meta class for IngredientFilter."""

        model = Ingredient
        fields = ('name',)
