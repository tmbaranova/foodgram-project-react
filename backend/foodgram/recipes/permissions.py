from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class SubscribePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (view.action == "list"
                and (obj.user == request.user or request.user.is_staff)
                or request.user.is_authenticated)
