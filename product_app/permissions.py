from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsProductManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Product Manager').exists()

class IsProductOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Product Owner').exists()

class IsEndUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='End User').exists()

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

# Combination
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff

class IsProductManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        is_manager = request.user.groups.filter(name='Product Manager').exists()
        return request.method in SAFE_METHODS or is_manager

class IsProductOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        is_owner = request.user.groups.filter(name='Product Owner').exists()
        return request.method in SAFE_METHODS or is_owner
