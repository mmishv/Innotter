from authentication.views import UserActionsViewSet
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"", UserActionsViewSet, basename="user-actions")

urlpatterns = [
    path("", include(router.urls)),
]
