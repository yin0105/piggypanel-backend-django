from django.apps import AppConfig
from superadmin.checks import check_admin_app, check_dependencies
from django.core import checks
from django.utils.translation import gettext_lazy as _


class SimpleAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_site = 'superadmin.sites.AdminSite'
    name = 'superadmin'
    verbose_name = _("SuperAdministration")

    def ready(self):
        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)


class AdminConfig(SimpleAdminConfig):
    """The default AppConfig for admin which does autodiscovery."""

    def ready(self):
        super().ready()
        self.module.autodiscover()
