from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.authtoken import views as authtoken_views

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    path('api/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/api-token-auth/', authtoken_views.obtain_auth_token, name='api-token-auth'),
    path('api/', include(router.urls)),
]