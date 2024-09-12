"""User models."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """User model."""

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="адрес электронной почты"
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Никнейм",
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message="Никнейм может содержать только буквы, цифры и @/./+/-/_."
        )]
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """Meta class for User."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

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
