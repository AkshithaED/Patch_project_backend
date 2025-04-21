from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsProductManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'product_manager'


class IsProductOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'product_owner'


class IsEndUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'end_user'


class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS to all authenticated users

        if request.user.is_staff:
            return True  # Admin

        if request.user.groups.filter(name='Product Manager').exists():
            return True  # Product Manager

        return False


class PatchPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS to all authenticated users

        if request.user.is_staff:
            return True  # Admin

        if request.user.groups.filter(name='Product Manager').exists():
            return True  # Product Manager

        return False


class ReleasePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS to all authenticated users

        if request.user.is_staff:
            return True  # Admin

        if request.user.groups.filter(name='Product Manager').exists():
            return True  # Product Manager

        return False


class ImagePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        elif request.user.role == 'product_owner':
            return obj.product in request.user.product_set.all() and request.method != 'DELETE'
        elif request.user.role == 'end_user':
            return request.method in SAFE_METHODS
        return False


class SecurityIssuePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        elif request.user.role == 'product_owner':
            return obj.image.product in request.user.product_set.all() and request.method != 'DELETE'
        elif request.user.role == 'end_user':
            return request.method in SAFE_METHODS
        return False
