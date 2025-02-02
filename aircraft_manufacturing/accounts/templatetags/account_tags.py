from django import template
from accounts.utils import get_user_display_name
from accounts.models import TeamMember

register = template.Library()

@register.filter
def display_name(user):
    """Template filter to display user name"""
    return get_user_display_name(user)

@register.filter
def can_create_parts(user):
    """Check if user can create parts based on their team membership"""
    if not hasattr(user, 'teammember'):
        return False
    teammember: TeamMember = user.teammember
    return teammember.team.has_create_perm()
