from rest_framework.permissions import BasePermission, SAFE_METHODS

class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Admin can do anything
        if user.role == 'admin':
            return True

        # Read-only access for others
        if request.method in SAFE_METHODS:
            return True

        # Product Manager can create/update (not delete)
        return user.role == 'product_manager'

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        if user.role == 'product_manager':
            return request.method in ['GET', 'PUT', 'PATCH']

        return False


class ImagePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        if request.method in SAFE_METHODS:
            return True

        return user.role in ['product_manager', 'product_owner']

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        if user.role in ['product_manager', 'product_owner']:
            return obj.product in user.product_set.all() and request.method in ['GET', 'PUT', 'PATCH']

        return request.method in SAFE_METHODS


class SecurityIssuePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        if request.method in SAFE_METHODS:
            return True

        return user.role in ['product_manager', 'product_owner']

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        if user.role in ['product_manager', 'product_owner']:
            return obj.image.product in user.product_set.all() and request.method in ['GET', 'PUT', 'PATCH']

        return request.method in SAFE_METHODS


class PatchPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        return request.method == 'GET'


class ReleasePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True

        return request.method == 'GET'
