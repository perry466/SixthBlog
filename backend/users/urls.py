from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/user/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/profile/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/create/', views.AdminUserCreateView.as_view(), name='admin-user-create'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
]
