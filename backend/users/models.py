"""User models."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (DEFAULT_EMAIL_MAX_LENGTH, FIRST_NAME_MAX_LENGTH,
                             LAST_NAME_MAX_LENGTH, USERNAME_MAX_LENGTH)
from users.validators import username_regex_validator, validate_username_not_me


class User(AbstractUser):
    """User model."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=DEFAULT_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name="адрес электронной почты"
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name="Никнейм",
        validators=[
            username_regex_validator,
            validate_username_not_me
        ]
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        verbose_name="Фамилия"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    class Meta:
        """Meta class for User."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']

    def __str__(self):
        """Return username."""
        return self.username


class Subscription(models.Model):
    """User subscription model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        """Meta class for Subscription."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        """Return subscription string."""
        return f'{self.user.username} подписан на {self.author.username}'
