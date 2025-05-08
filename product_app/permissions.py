# from rest_framework.permissions import BasePermission, SAFE_METHODS
 
# class ProductPermission(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user.role in ['admin', 'product_manager']
 
 
# class ImagePermission(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user.role in ['admin', 'product_manager', 'product_owner']
 
#     def has_object_permission(self, request, view, obj):
#         if request.user.role == 'admin':
#             return True
#         elif request.user.role == 'product_manager':
#             return True
#         elif request.user.role == 'product_owner':
#             return (
#                 obj.product in request.user.product_set.all() and
#                 request.method in ['GET', 'POST', 'PUT', 'PATCH']
#             )
#         elif request.user.role == 'end_user':
#             return request.method in SAFE_METHODS
#         return False
 
 
# class SecurityIssuePermission(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user.role in ['admin', 'product_manager', 'product_owner']
 
#     def has_object_permission(self, request, view, obj):
#         if request.user.role == 'admin':
#             return True
#         elif request.user.role == 'product_manager':
#             return True
#         elif request.user.role == 'product_owner':
#             return (
#                 obj.image.product in request.user.product_set.all() and
#                 request.method in ['GET', 'POST', 'PUT', 'PATCH']
#             )
#         elif request.user.role == 'end_user':
#             return request.method in SAFE_METHODS
#         return False
 
 
# class PatchPermission(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         return request.user.role == 'admin'
 
 
# class ReleasePermission(BasePermission):
#     def has_permission(self, request, view):
#         return request.method in SAFE_METHODS or request.user.role == 'admin'

from rest_framework.permissions import BasePermission, SAFE_METHODS

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        # Admin can perform any operation, including DELETE
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # For other users, only safe methods (GET, HEAD, OPTIONS) are allowed
        if request.method in SAFE_METHODS:
            return True

        # Product Manager can perform POST, PUT, PATCH (but cannot DELETE)
        return request.user.role == 'product_manager'

    def has_object_permission(self, request, view, obj):
        # Admin can access any product, including DELETE
        if request.user.role == 'admin':
            return True

        # Product Manager can view or edit products (but cannot DELETE)
        if request.user.role == 'product_manager':
            return request.method in ['GET', 'PUT', 'PATCH']
        
        return False


class ImagePermission(BasePermission):
    def has_permission(self, request, view):
        # Admin can perform any operation, including DELETE
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # For other users, only safe methods (GET, HEAD, OPTIONS) are allowed
        if request.method in SAFE_METHODS:
            return True
        
        # Product Manager and Product Owner can create and update images, but cannot delete
        return request.user.role in ['product_manager', 'product_owner']

    def has_object_permission(self, request, view, obj):
        # Admin can access any image, including DELETE
        if request.user.role == 'admin':
            return True

        # Product Manager and Product Owner can manage their own images
        if request.user.role in ['product_manager', 'product_owner']:
            return obj.product in request.user.product_set.all() and request.method in ['GET', 'PUT', 'PATCH']

        # End Users can only view images (safe methods)
        return request.method in SAFE_METHODS


class SecurityIssuePermission(BasePermission):
    def has_permission(self, request, view):
        # Admin can perform any operation, including DELETE
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # For other users, only safe methods (GET, HEAD, OPTIONS) are allowed
        if request.method in SAFE_METHODS:
            return True
        
        # Product Manager and Product Owner can create and update security issues, but cannot delete
        return request.user.role in ['product_manager', 'product_owner']

    def has_object_permission(self, request, view, obj):
        # Admin can access any security issue, including DELETE
        if request.user.role == 'admin':
            return True

        # Product Manager and Product Owner can manage security issues
        if request.user.role in ['product_manager', 'product_owner']:
            return obj.image.product in request.user.product_set.all() and request.method in ['GET', 'PUT', 'PATCH']

        # End Users can only view security issues (safe methods)
        return request.method in SAFE_METHODS


class PatchPermission(BasePermission):
    def has_permission(self, request, view):
        # Admin can perform any operation, including DELETE
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # For other users, only safe methods (GET, HEAD, OPTIONS) are allowed
        if request.method in SAFE_METHODS:
            return True
        
        # Only Admin can delete patches
        return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        # Admin can access any patch, including DELETE
        if request.user.role == 'admin':
            return True

        # For all other users, only GET is allowed (no DELETE)
        return request.method == 'GET'


class ReleasePermission(BasePermission):
    def has_permission(self, request, view):
        # Admin can perform any operation, including DELETE
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        # For other users, only safe methods (GET, HEAD, OPTIONS) are allowed
        if request.method in SAFE_METHODS:
            return True

        # Only Admin can delete releases
        return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        # Admin can access any release, including DELETE
        if request.user.role == 'admin':
            return True

        # For all other users, only GET is allowed (no DELETE)
        return request.method == 'GET'
