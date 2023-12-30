from rest_framework import permissions

class IsUserManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.groups.filter(name='Manager').exists():
            return True
        else:
            return False
        
class IsUserManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager').exists():
            return True
        else:
            return False