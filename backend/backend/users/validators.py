import re

from django.core.exceptions import ValidationError


def username_validator(value):
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы.'
        )
    if value == 'me':
        raise ValidationError(
            'Имя пользователя "me" недопустимо.'
        )
    return value
