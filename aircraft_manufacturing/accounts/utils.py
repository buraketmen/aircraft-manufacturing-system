from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from django.contrib.auth.models import User

def get_user_display_name(user: User) -> str:
    """Get the best available display name for a user"""
    if not user:
        return 'N/A'
    first_name = getattr(user, 'first_name', '').strip()
    last_name = getattr(user, 'last_name', '').strip()
    email = getattr(user, 'email', '').strip()
    username = getattr(user, 'username', 'N/A').strip()
    if first_name and last_name:
        return f"{user.first_name} {user.last_name}"
    if first_name:
        return first_name
    if last_name:
        return last_name
    if email:
        return email.split('@')[0]
    return username