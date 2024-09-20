"""Recipes admin."""

from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    """Inline class for RecipeIngredient model."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe model admin."""

    list_display = ('pk', 'name', 'author', 'favorite_count')
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username', 'ingredients__name')
    inlines = (RecipeIngredientInline,)

    @admin.display(
        description='Number of adds to favorites',
        ordering='favorites__count'
    )
    def favorite_count(self, obj):
        """Get the count of user's favorites."""
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag model admin."""

    list_display = ('pk', 'name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ingredient model admin."""

    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Favorite model admin."""

    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """ShoppingCart model admin."""

    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
