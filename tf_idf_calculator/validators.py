import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extension = '.txt'
    if ext.lower() != valid_extension:
        raise ValidationError('Загрузите в формате .txt')