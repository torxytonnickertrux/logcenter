from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from django.views.generic import TemplateView
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .serializers import IngestSerializer, LogEntrySerializer
from .authentication import BearerTokenAuthentication
from .services import ingest, filter_logs
from .models import LogEntry, System

@method_decorator(csrf_exempt, name="dispatch")
class IngestView(APIView):
    authentication_classes = []

    @extend_schema(
        request=IngestSerializer,
        responses={200: {"type": "object"}},
        parameters=[OpenApiParameter(name="Authorization", location=OpenApiParameter.HEADER, required=True, description="Bearer <LOG_INGEST_TOKEN>")],
        examples=[OpenApiExample("payload", value={"host": "vilksonvtch.pythonanywhere.com", "type": "access", "message": "line", "hash": "sha256", "timestamp": 1735532123.123})],
        auth=["bearerAuth"],
    )
    @method_decorator(csrf_exempt)
    def post(self, request):
        s = IngestSerializer(data=request.data)
        if not s.is_valid():
            return Response({"detail": "invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        auth = request.headers.get("Authorization") or ""
        prefix = "Bearer "
        if not auth.startswith(prefix):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth[len(prefix):].strip()
        from hashlib import sha256
        token_hash = sha256(token.encode("utf-8")).hexdigest()
        try:
            from .models import LogIngestToken
            tok = LogIngestToken.objects.select_related("system").get(token_hash=token_hash)
        except LogIngestToken.DoesNotExist:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        if not tok.is_valid():
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        system = tok.system
        result, obj = ingest(system, s.validated_data)
        if result == "duplicate":
            return Response({"status": "duplicate"})
        return Response({"status": "ok"})

class LogsView(APIView):
    authentication_classes = []

    @extend_schema(
        responses={200: LogEntrySerializer(many=True)},
        parameters=[
            OpenApiParameter(name="host", location=OpenApiParameter.QUERY),
            OpenApiParameter(name="type", location=OpenApiParameter.QUERY),
            OpenApiParameter(name="level", location=OpenApiParameter.QUERY),
            OpenApiParameter(name="since", location=OpenApiParameter.QUERY),
            OpenApiParameter(name="until", location=OpenApiParameter.QUERY),
            OpenApiParameter(name="limit", location=OpenApiParameter.QUERY),
            OpenApiParameter(name="Authorization", location=OpenApiParameter.HEADER, required=True, description="Bearer <LOG_INGEST_TOKEN>"),
        ],
        auth=["bearerAuth"],
    )
    def get(self, request):
        auth = request.headers.get("Authorization") or ""
        prefix = "Bearer "
        if not auth.startswith(prefix):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth[len(prefix):].strip()
        from hashlib import sha256
        token_hash = sha256(token.encode("utf-8")).hexdigest()
        try:
            from .models import LogIngestToken
            tok = LogIngestToken.objects.select_related("system").get(token_hash=token_hash)
        except LogIngestToken.DoesNotExist:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        if not tok.is_valid():
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        system = tok.system
        qs = filter_logs(system, request.query_params)
        return Response(LogEntrySerializer(qs, many=True).data)

class HealthView(APIView):
    @extend_schema(responses={200: {"type": "object"}})
    def get(self, request):
        return Response({"status": "healthy"})

class DashboardOverviewView(TemplateView):
    template_name = "core/dashboard.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        totals = LogEntry.objects.values("system__slug", "level").annotate(total=Count("id")).order_by()
        latest_critical = LogEntry.objects.filter(level=LogEntry.LEVEL_CRITICAL).order_by("-received_at")[:10]
        hosts_fail = LogEntry.objects.filter(level__in=[LogEntry.LEVEL_ERROR, LogEntry.LEVEL_CRITICAL]).values("system__slug", "host").annotate(total=Count("id")).order_by("-total")[:10]
        ctx["totals"] = list(totals)
        ctx["latest_critical"] = latest_critical
        ctx["hosts_fail"] = list(hosts_fail)
        return ctx

class HomeView(TemplateView):
    template_name = "core/home.html"
