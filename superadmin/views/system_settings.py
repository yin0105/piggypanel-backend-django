from django.http import Http404, JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from superadmin.forms import SystemSettingsForm


class SystemSettingsView(FormView):
    """
    Display the login form and handle the login action.
    """
    form_class = SystemSettingsForm
    template_name = 'superadmin/system_settings.html'

    # @method_decorator(sensitive_post_parameters())
    # @method_decorator(csrf_protect)
    # @method_decorator(never_cache)
    # def dispatch(self, request, *args, **kwargs):
    #     if self.redirect_authenticated_user and self.request.user.is_authenticated:
    #         redirect_to = self.get_success_url()
    #         if redirect_to == self.request.path:
    #             raise ValueError(
    #                 "Redirection loop for authenticated user detected. Check that "
    #                 "your LOGIN_REDIRECT_URL doesn't point to a login page."
    #             )
    #         return HttpResponseRedirect(redirect_to)
    #     return super().dispatch(request, *args, **kwargs)

    # def get_success_url(self):
    #     url = self.get_redirect_url()
    #     return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    # def get_redirect_url(self):
    #     """Return the user-originating redirect URL if it's safe."""
    #     redirect_to = self.request.POST.get(
    #         self.redirect_field_name,
    #         self.request.GET.get(self.redirect_field_name, '')
    #     )
    #     url_is_safe = url_has_allowed_host_and_scheme(
    #         url=redirect_to,
    #         allowed_hosts=self.get_success_url_allowed_hosts(),
    #         require_https=self.request.is_secure(),
    #     )
    #     return redirect_to if url_is_safe else ''

    # def get_form_class(self):
    #     return self.authentication_form or self.form_class

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['request'] = self.request
    #     return kwargs

    # def form_valid(self, form):
    #     """Security check complete. Log the user in."""
    #     auth_login(self.request, form.get_user())
    #     return HttpResponseRedirect(self.get_success_url())

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     current_site = get_current_site(self.request)
    #     context.update({
    #         self.redirect_field_name: self.get_redirect_url(),
    #         'site': current_site,
    #         'site_name': current_site.name,
    #         **(self.extra_context or {})
    #     })
    #     return context
