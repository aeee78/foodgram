"""Recipes models."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import MAX_INGREDIENT_AMOUNT
from recipes.constants import (INGREDIENT_MEASUREMENT_MAX_LENGTH,
                               INGREDIENT_NAME_MAX_LENGTH, NAME_MAX_LENGTH,
                               RECIPE_MIN_AMOUNT, RECIPE_MIN_COOKING_TIME,
                               TAG_NAME_MAX_LENGTH, TAG_SLUG_MAX_LENGTH)
from users.models import User


class Recipe(models.Model):
    """Recipe model."""

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Название рецепта"
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name="Изображение рецепта"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(RECIPE_MIN_COOKING_TIME)],
        verbose_name="Время приготовления в минутах"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор рецепта"
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name="Ингредиенты"
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name="Теги"
    )
    shopping_carts = models.ManyToManyField(
        'ShoppingCart',
        related_name='recipes',
        blank=True
    )

    class Meta:
        """Meta class for Recipe."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['name']

    def __str__(self):
        """Return name."""
        return self.name


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True,
                            verbose_name="Название тега")
    slug = models.SlugField(max_length=TAG_SLUG_MAX_LENGTH, unique=True,
                            verbose_name="Слаг тега")

    class Meta:
        """Meta class for Tag."""

        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        """Return name."""
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_MAX_LENGTH,
        verbose_name="Единица измерения"
    )

    class Meta:
        """Meta class for Ingredient."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]
        ordering = ['name']

    def __str__(self):
        """Return name and measurement unit."""
        return f"{self.name}, {self.measurement_unit}"


class RecipeIngredient(models.Model):
    """RecipeIngredient model."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(RECIPE_MIN_AMOUNT),
            MaxValueValidator(MAX_INGREDIENT_AMOUNT)
        ],
        verbose_name="Количество"
    )

    class Meta:
        """Meta class for RecipeIngredient."""

        verbose_name = "Рецепт - ингредиент"
        verbose_name_plural = "Рецепты - ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        ordering = ['recipe']

    def __str__(self):
        """Return recipe and ingredient."""
        return (
            f"{self.recipe.name} - {self.ingredient.name}: "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """Favorite model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Избранный рецепт"
    )

    class Meta:
        """Meta class for Favorite."""

        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]
        ordering = ['recipe__name']

    def __str__(self):
        """Return user and recipe."""
        return f"{self.user.username} favorited {self.recipe.name}"


class ShoppingCart(models.Model):
    """ShoppingCart model."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_shopping_carts',
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_shopping_carts',
        verbose_name="Рецепт"
    )

    class Meta:
        """Meta class for ShoppingCart."""

        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзина покупок"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]
        ordering = ['recipe__name']

    def __str__(self):
        """Return user and recipe."""
        return f"{self.user.username}'s cart - {self.recipe.name}"
