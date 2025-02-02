from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Team, TeamType, TeamMember

admin.site.unregister(User)

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ['user']

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [TeamMemberInline]
    search_fields = ['username', 'first_name', 'last_name', 'email']

@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('name',)

    def has_change_permission(self, *args ,**kwargs) -> bool:
        return False


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('name',)

    
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'created_at', 'updated_at')
    list_filter = ('team',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
