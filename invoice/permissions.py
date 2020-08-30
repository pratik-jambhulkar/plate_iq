from rest_framework.permissions import BasePermission


class InvoicePermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['digitize', 'create', 'update', 'partial_update'] and not request.user.is_superuser:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return True
