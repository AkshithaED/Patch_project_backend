# urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ReleaseViewSet, ProductViewSet, ImageViewSet,
    SecurityIssueViewSet, PatchViewSet, JarViewSet,
    HighLevelScopeViewSet, patch_completion_percentage,patch_product_completion_status, update_patch_data, 
    patch_product_jars_list, update_patch_product_jar, build_image_url_endpoint
)

release_list = ReleaseViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

release_detail = ReleaseViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

patch_list = PatchViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

patch_detail = PatchViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

product_list = ProductViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

product_detail = ProductViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

image_list = ImageViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

image_detail = ImageViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

security_issue_list = SecurityIssueViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

security_issue_detail = SecurityIssueViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

jar_list = JarViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

jar_detail = JarViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

high_level_scope_list = HighLevelScopeViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

high_level_scope_detail = HighLevelScopeViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('releases/', release_list, name='release-list'),
    path('releases/<str:name>/', release_detail, name='release-detail'),
    path('patches/', patch_list, name='patch-list'),
    path('patches/update-data/', update_patch_data, name='update-patch-data'),
    path('patches/<str:name>/', patch_detail, name='patch-detail'),
    path('patches/<str:name>/completion/', patch_completion_percentage, name='patch-completion'),
    path('patches/<str:name>/product-completion/', patch_product_completion_status, name='patch-product-completion'),
    path('products/', product_list, name='product-list'),
    path('products/<str:name>/', product_detail, name='product-detail'),
    path('images/', image_list, name='image-list'),
    path('images/<str:image_name>/<str:build_number>/', image_detail, name='image-detail'),
    path('security-issues/', security_issue_list, name='security-issue-list'),
    path('security-issues/<str:cve_id>/', security_issue_detail, name='security-issue-detail'),
    path('jars/', jar_list, name='jar-list'),
    path('jars/<str:name>/', jar_detail, name='jar-detail'),
    path('high-level-scopes/', high_level_scope_list, name='high-level-scope-list'),
    path('high-level-scopes/<str:name>/', high_level_scope_detail, name='high-level-scope-detail'),
    path('patchproductjars/<str:patch_name>/<str:product_name>/', patch_product_jars_list),
    path('patchproductjars/<str:patch_name>/<str:product_name>/<str:jar_name>/', update_patch_product_jar),
    path('build-image-url/', build_image_url_endpoint, name='build-image-url'),
]
