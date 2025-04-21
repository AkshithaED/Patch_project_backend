from rest_framework.permissions import BasePermission, SAFE_METHODS

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'product_manager']


class ImagePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'product_manager', 'product_owner']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        elif request.user.role == 'product_manager':
            return True
        elif request.user.role == 'product_owner':
            return (
                obj.product in request.user.product_set.all() and 
                request.method in ['GET', 'POST', 'PUT', 'PATCH']
            )
        elif request.user.role == 'end_user':
            return request.method in SAFE_METHODS
        return False


class SecurityIssuePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'product_manager', 'product_owner']

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        elif request.user.role == 'product_manager':
            return True
        elif request.user.role == 'product_owner':
            return (
                obj.image.product in request.user.product_set.all() and 
                request.method in ['GET', 'POST', 'PUT', 'PATCH']
            )
        elif request.user.role == 'end_user':
            return request.method in SAFE_METHODS
        return False


class PatchPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'admin'


class ReleasePermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.role == 'admin'
