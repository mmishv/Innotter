from django.urls import include, path
from pages import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register(r"tags", views.TagViewSet)
router.register("", views.PageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
