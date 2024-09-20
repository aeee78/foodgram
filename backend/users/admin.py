"""Users admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """User model admin."""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'recipe_count',
        'subscriber_count',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def recipe_count(self, obj):
        """Get the count of user's recipes."""
        return obj.recipes.count()
    recipe_count.short_description = 'Recipe count'

    def subscriber_count(self, obj):
        """Get the count of user's subscribers."""
        return obj.subscribers.count()
    subscriber_count.short_description = 'Subscriber count'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription model admin."""

    list_display = ('pk', 'user', 'author')
    search_fields = ('user__username', 'author__username')
