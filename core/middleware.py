import re

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.middleware.csrf import CsrfViewMiddleware

# Cloudflare quick-tunnel hostnames change every run; trust them only in DEBUG.
_TRYCF_ORIGIN = re.compile(
    r'^https://[a-z0-9]+(?:-[a-z0-9]+)*\.trycloudflare\.com$',
    re.IGNORECASE,
)


class TunnelCsrfMiddleware(CsrfViewMiddleware):
    """Allow CSRF from Cloudflare quick tunnels during local demo sharing."""

    def _origin_verified(self, request):
        origin = request.META.get('HTTP_ORIGIN', '')
        if origin and _TRYCF_ORIGIN.match(origin):
            if settings.DEBUG or getattr(settings, 'ALLOW_CLOUDFLARE_TUNNEL', False):
                return True
        return super()._origin_verified(request)


class DemoAutoLoginMiddleware:
    """Sign in the first superuser when LOGIN_REQUIRED is disabled (demo mode)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            user = get_user_model().objects.filter(is_superuser=True).first()
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return self.get_response(request)
