from superadmin.decorators import register
from superadmin.filters import (
    AllValuesFieldListFilter, BooleanFieldListFilter, ChoicesFieldListFilter,
    DateFieldListFilter, EmptyFieldListFilter, FieldListFilter, ListFilter,
    RelatedFieldListFilter, RelatedOnlyFieldListFilter, SimpleListFilter,
)
from superadmin.options import (
    HORIZONTAL, VERTICAL, ModelAdmin, StackedInline, TabularInline,
)
from superadmin.sites import AdminSite, site
from django.utils.module_loading import autodiscover_modules

__all__ = [
    "register", "ModelAdmin", "HORIZONTAL", "VERTICAL", "StackedInline",
    "TabularInline", "AdminSite", "site", "ListFilter", "SimpleListFilter",
    "FieldListFilter", "BooleanFieldListFilter", "RelatedFieldListFilter",
    "ChoicesFieldListFilter", "DateFieldListFilter",
    "AllValuesFieldListFilter", "EmptyFieldListFilter",
    "RelatedOnlyFieldListFilter", "autodiscover",
]


def autodiscover():
    autodiscover_modules('superadmin', register_to=site)


default_app_config = 'superadmin.apps.AdminConfig'
