from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    ReleaseViewSet, PatchViewSet, ProductViewSet, ImageViewSet, SecurityIssueViewSet,
    NestedPatchListView, NestedProductListView, NestedImageListView, SecurityIssueByImageView, SoftDeletePatchView
)

router = DefaultRouter()
router.register(r'releases', ReleaseViewSet)
router.register(r'patches', PatchViewSet)
router.register(r'products', ProductViewSet)
router.register(r'images', ImageViewSet)
router.register(r'security-issues', SecurityIssueViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('<str:release_name>/', NestedPatchListView.as_view()),
#     path('<str:release_name>/<str:patch_name>/', NestedProductListView.as_view()),
#     path('<str:release_name>/<str:patch_name>/<str:product_name>/', NestedImageListView.as_view()),
#     path('<str:release_name>/<str:patch_name>/<str:product_name>/<str:build_number>/',
#          SecurityIssueByImageView.as_view()),
#     path('patches/<str:pk>/soft-delete/', SoftDeletePatchView.as_view(), name='soft-delete-patch'),
# ]

urlpatterns = [
    path('', include(router.urls)),
    path('patches/<str:pk>/soft-delete/', SoftDeletePatchView.as_view(), name='soft-delete-patch'), 
    path('<str:release_name>/', NestedPatchListView.as_view()),
    path('<str:release_name>/<str:patch_name>/', NestedProductListView.as_view()),
    re_path(r'^(?P<release_name>[^/]+)/(?P<patch_name>[^/]+)/(?P<product_name>[^/]+)/$', NestedImageListView.as_view(), name='nested-image-list'),
    path('<str:release_name>/<str:patch_name>/<str:product_name>/<str:build_number>/', SecurityIssueByImageView.as_view()),
]
