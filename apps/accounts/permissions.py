from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'client') and obj.client == request.user:
            return True
        if hasattr(obj, 'master') and hasattr(request.user, 'master_profile'):
            return obj.master_id == request.user.master_profile.id
        owner = getattr(obj, 'user', None)
        return owner == request.user


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
