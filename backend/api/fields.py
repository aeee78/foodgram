import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Custom serializer field for handling base64 encoded images."""

    def to_internal_value(self, data: str) -> ContentFile:
        """Convert base64-encoded image data to ContentFile."""
        if isinstance(data, str) and data.startswith('data:image'):
            format_data, imgstr = data.split(';base64,')
            ext = format_data.split('/')[-1]
            return ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)
