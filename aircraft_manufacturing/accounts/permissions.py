from rest_framework import permissions

class AllowAny(permissions.BasePermission):
    """
    Custom permission to allow any request.
    """
    def has_permission(self, request, view):
        return True

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers to edit.
    Read permissions are allowed for any authenticated user,
    but write operations require superuser status.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to superusers
        return request.user and request.user.is_superuser 

class IsMemberOfTeam(permissions.BasePermission):
    """
    Custom permission to only allow team members to edit.
    Read permissions are allowed for any authenticated user,
    but write operations require team member status.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to team members
        return request.user and hasattr(request.user, 'teammember')

class IsMemberOfAssemblyTeam(permissions.BasePermission):
    """
    Custom permission to only allow assembly team to edit.
    Read permissions are allowed for any authenticated user,
    but write operations require assembler status.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to assemblers
        teammember = getattr(request.user, 'teammember', None)
        return request.user and teammember and teammember.team.can_create_aircraft()