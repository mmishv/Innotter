from django.urls import include, path
from posts.views import PostViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register("", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
