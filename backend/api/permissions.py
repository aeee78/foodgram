"""Permissions for the API application."""

from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """Admin and author permissions."""

    def has_permission(self, request, view):
        """Admin and author permissions."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Admin and author permissions."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)
