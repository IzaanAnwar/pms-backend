from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Organization


def generate_unique_organization_slug(*, organization_name: str) -> str:
    base_slug = slugify(organization_name)
    if not base_slug:
        raise ValidationError('Invalid organization name')

    slug_field = Organization._meta.get_field('slug')
    max_length = slug_field.max_length

    base_slug = base_slug[:max_length]

    if not Organization.all_objects.filter(slug=base_slug).exists():
        return base_slug

    for i in range(2, 1000):
        suffix = f'-{i}'
        prefix = base_slug[: max_length - len(suffix)]
        candidate = f'{prefix}{suffix}'

        if not Organization.all_objects.filter(slug=candidate).exists():
            return candidate

    raise ValidationError('Unable to generate a unique organization slug')
