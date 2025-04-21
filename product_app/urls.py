from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .models import CustomUser

# from ProductManagement.product_app import admin
# from ProductManagement.product_app import admin
from product_app.models import CustomUser
from .views import (
    ReleaseViewSet, PatchViewSet, ProductViewSet, ImageViewSet, SecurityIssueViewSet,
    NestedPatchListView, NestedProductListView, NestedImageListView, SecurityIssueByImageView
)
# admin.site.register(CustomUser)

router = DefaultRouter()
router.register(r'releases', ReleaseViewSet)
router.register(r'patches', PatchViewSet)
router.register(r'products', ProductViewSet)
router.register(r'images', ImageViewSet)
router.register(r'security-issues', SecurityIssueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<str:release_name>/', NestedPatchListView.as_view()),
    path('<str:release_name>/<str:patch_name>/', NestedProductListView.as_view()),
    path('<str:release_name>/<str:patch_name>/<str:product_name>/', NestedImageListView.as_view()),
    path('<str:release_name>/<str:patch_name>/<str:product_name>/<str:build_number>/',
         SecurityIssueByImageView.as_view()),
]
