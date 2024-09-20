from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from users.constants import FORBIDDEN_USERNAME

username_regex_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=_("Никнейм может содержать только буквы, цифры и @/./+/-/_.")
)


def validate_username_not_me(value):
    """Validate that the username is not forbidden."""
    if value == FORBIDDEN_USERNAME:
        raise ValidationError(
            _(f'Никнейм не может быть "{FORBIDDEN_USERNAME}".'),
            params={'value': value},
        )
