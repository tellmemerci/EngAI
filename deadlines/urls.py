from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeadlineViewSet

app_name = 'deadlines'

router = DefaultRouter()
router.register(r'', DeadlineViewSet, basename='deadline')

urlpatterns = [
    path('api/', include(router.urls)),
]