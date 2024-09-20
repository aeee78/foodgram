"""Permissions for the API application."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow write access only to the author of the object."""

    def has_object_permission(self, request, view, obj):
        """Allow write access only to the author of the object."""
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
