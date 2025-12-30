import os
from types import SimpleNamespace
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class BearerTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization") or ""
        prefix = "Bearer "
        if not auth.startswith(prefix):
            raise AuthenticationFailed("Missing bearer token")
        token = auth[len(prefix):].strip()
        expected = os.environ.get("LOG_INGEST_TOKEN", "dev-token")
        if token != expected:
            raise AuthenticationFailed("Invalid token")
        user = SimpleNamespace(is_authenticated=True, username="token")
        return (user, token)

class DummyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None
