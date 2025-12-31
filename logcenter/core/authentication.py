import hashlib
from types import SimpleNamespace
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import LogIngestToken

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

class BearerTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization") or ""
        prefix = "Bearer "
        if not auth.startswith(prefix):
            raise AuthenticationFailed("Missing bearer token")
        token = auth[len(prefix):].strip()
        token_hash = _hash_token(token)
        try:
            tok = LogIngestToken.objects.select_related("system").get(token_hash=token_hash)
        except LogIngestToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")
        if not tok.is_valid():
            raise AuthenticationFailed("Invalid token")
        from django.utils import timezone
        tok.last_used_at = timezone.now()
        tok.save(update_fields=["last_used_at"])
        user = SimpleNamespace(is_authenticated=True, username=f"system:{tok.system.slug}")
        request.system = tok.system
        request.ingest_token = tok
        return (user, token)
