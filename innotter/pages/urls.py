from django.urls import include, path
from pages import views
from posts.views import PostViewSet
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = SimpleRouter()

router.register(r"pages", views.PageViewSet)
router.register(r"tags", views.TagViewSet)

nested_router = routers.NestedSimpleRouter(
    router, parent_prefix=r"pages", lookup="page"
)
nested_router.register(r"posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
]
