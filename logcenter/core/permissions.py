import os
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed

class IngestTokenPermission(BasePermission):
    def has_permission(self, request, view):
        auth = request.headers.get("Authorization") or ""
        prefix = "Bearer "
        if not auth.startswith(prefix):
            raise AuthenticationFailed()
        token = auth[len(prefix):].strip()
        expected = os.environ.get("LOG_INGEST_TOKEN", "dev-token")
        if token != expected:
            raise AuthenticationFailed()
        return True
