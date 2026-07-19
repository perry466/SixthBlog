from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.SetupStatusView.as_view(), name='setup-status'),
    path('check-db/', views.CheckDatabaseView.as_view(), name='setup-check-db'),
    path('install/', views.InstallView.as_view(), name='setup-install'),
]
