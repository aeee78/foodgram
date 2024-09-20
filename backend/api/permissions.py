"""Permissions for the API application."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow write access only to the author of the object."""

    def has_object_permission(self, request, view, obj):
        """Allow write access only to the author of the object."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
