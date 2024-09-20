"""Utility functions and classes for handling recipes and ingredients."""


from typing import Type

from django.db.models import Model
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from recipes.models import RecipeIngredient


def create_ingredients(ingredients, recipe):
    """Create RecipeIngredient instances for a given recipe."""
    recipe_ingredients = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        )
        for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(recipe_ingredients)


def create_model_instance(

    request: Request,
    instance: Model,
    serializer_class: Type[serializers.ModelSerializer]
) -> Response:
    """Create a model instance."""
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
    """Delete a model instance."""
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
