"""Recipes models."""

from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from users.models import User


class Recipe(models.Model):
    """Recipe model."""

    name = models.CharField(max_length=256, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name="Изображение рецепта"
    )
    text = models.TextField(verbose_name="Описание рецепта")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
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
        related_name='recipes_in_cart',
        blank=True
    )

    class Meta:
        """Meta class for Recipe."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        """Return name."""
        return self.name


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(max_length=32, unique=True,
                            verbose_name="Название тега")
    slug = models.SlugField(max_length=32, unique=True,
                            verbose_name="Слаг тега")

    class Meta:
        """Meta class for Tag."""

        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        """Return name."""
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=128, verbose_name="Название ингредиента")
    measurement_unit = models.CharField(
        max_length=64, verbose_name="Единица измерения")

    class Meta:
        """Meta class for Ingredient."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]

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
        validators=[MinValueValidator(1)], verbose_name="Количество"
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
        related_name='favorited_by',
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

    def __str__(self):
        """Return user and recipe."""
        return f"{self.user.username} favorited {self.recipe.name}"


class ShoppingCart(models.Model):
    """ShoppingCart model."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
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

    def __str__(self):
        """Return user and recipe."""
        return f"{self.user.username}'s cart - {self.recipe.name}"
