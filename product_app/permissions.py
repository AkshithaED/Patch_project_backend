from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsProductManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Product Manager').exists()

class IsProductOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Product Owner').exists()

class EndUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='End User').exists()
