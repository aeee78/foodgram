from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

username_regex_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=_("Никнейм может содержать только буквы, цифры и @/./+/-/_.")
)


def validate_username_not_me(value):
    """Validate that the username is not "me"."""
    if value.lower() == 'me':
        raise ValidationError(
            _('Никнейм не может быть "me".'),
            params={'value': value},
        )
