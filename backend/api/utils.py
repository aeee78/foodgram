"""Utility functions and classes for handling recipes and ingredients."""

import base64
from typing import List, Type

from django.core.files.base import ContentFile
from django.db.models import Model
from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from recipes.models import Ingredient, RecipeIngredient, Recipe


class Base64ImageField(serializers.ImageField):
    """Custom serializer field for handling base64 encoded images."""

    def to_internal_value(self, data: str) -> ContentFile:
        """
        Convert base64-encoded image data to ContentFile.

        Args:
            data: Base64-encoded image data.

        Returns:
            ContentFile object containing the decoded image data.
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format_data, imgstr = data.split(';base64,')
            ext = format_data.split('/')[-1]
            return ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


def create_ingredients(ingredients: List[dict], recipe: Recipe) -> None:
    """
    Create RecipeIngredient instances for a given recipe.

    Args:
        ingredients: List of dictionaries containing ingredient data.
        recipe: Recipe instance to associate ingredients with.
    """
    ingredient_list = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
            amount=ingredient['amount']
        )
        for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(ingredient_list)


def create_model_instance(
    request: Request,
    instance: Model,
    serializer_class: Type[serializers.ModelSerializer]
) -> Response:
    """
    Create a model instance (e.g., add recipe to favorites or shopping list).

    Args:
        request: Request object.
        instance: Model instance to be associated.
        serializer_class: Serializer class to be used.

    Returns:
        Response object with created data or error message.
    """
    serializer = serializer_class(
        data={'user': request.user.id, 'recipe': instance.id},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(
    request: Request,
    model_class: Type[Model],
    instance: Model,
    error_message: str
) -> Response:
    """
    Delete a model instance (e.g., remove recipe from favorites).

    Args:
        request: Request object.
        model_class: Model class to query.
        instance: Model instance to be deleted.
        error_message: Error message to be returned if instance doesn't exist.

    Returns:
        Response object with success status or error message.
    """
    if not model_class.objects.filter(
        user=request.user,
        recipe=instance
    ).exists():
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )

    model_class.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
