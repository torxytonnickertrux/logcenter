from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from logcenter.core.views import IngestView, LogsView, HealthView, DashboardOverviewView, HomeView

urlpatterns = [
    path("", HomeView.as_view()),
    path("admin/", admin.site.urls),
    path("api/ingest/", IngestView.as_view()),
    path("api/logs/", LogsView.as_view()),
    path("api/health/", HealthView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("dashboard/", DashboardOverviewView.as_view()),
]
