from typing import Optional
from rest_framework import viewsets, permissions, filters, status
from django.contrib.auth.models import User
from accounts.models import Team, TeamMember, TeamType
from accounts.serializers import UserSerializer, TeamSerializer, TeamMemberSerializer, TeamTypeSerializer
from accounts.permissions import IsSuperUserOrReadOnly
from accounts.constants import DEFAULT_TEAM_USERS, TeamTypes
from inventory.models import PartType
from assembly.models import AircraftType
from aircraft_manufacturing.responses import GeneralFailedResponseSerializer
from aircraft_manufacturing.pagination import DataTablePagination
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.views import LoginView
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.filters import TeamFilter, TeamMemberFilter, UserFilter, TeamTypeFilter
from inventory.models import TeamPartPermission

class HomeView(TemplateView):
    """Home page view with context data for the index template."""
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_member: Optional[TeamMember] = getattr(self.request.user, 'teammember', None)
        context['aircraft_types'] = [{'id': aircraft_type.id, 'name': aircraft_type.name} 
                                   for aircraft_type in AircraftType.objects.only('id', 'name').all()]
        context['part_types'] = [{'id': part_type.id, 'name': part_type.name} 
                                for part_type in PartType.objects.only('id', 'name').all()]
        context['user_has_team'] = team_member is not None
        context['can_assemble_aircraft'] = team_member.team.can_create_aircraft() if team_member else False
        context['craftable_parts'] = TeamPartPermission.objects.select_related('team_type').filter(
            team_type=team_member.team.team_type,
            can_create=True
        ) if team_member else []
        context['debug'] = settings.DEBUG
        return context


class CustomLoginView(LoginView):
    """Generic login view with custom template. Includes defeault users for faster testing."""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_users'] = DEFAULT_TEAM_USERS
        return context


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for managing users."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = UserFilter
    ordering_fields = ['date_joined']
    ordering = ['-date_joined']
    queryset = User.objects.prefetch_related(
        'teammember',
        'teammember__team'
    ).all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ['me', 'change_password']:
            return [permissions.IsAuthenticated()]
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List users",
        operation_description="Get a paginated list of all users",
        
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create user",
        operation_description="Create a new user",
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GeneralFailedResponseSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get user details",
        operation_description="Get detailed information about a specific user",
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GeneralFailedResponseSerializer
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update user",
        operation_description="Update user information",
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GeneralFailedResponseSerializer
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update user",
        operation_description="Update specific fields of user information",
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GeneralFailedResponseSerializer
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete user",
        operation_description="Delete a user account",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description='No content'),
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GeneralFailedResponseSerializer
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get current user",
        operation_description="Get information about the currently authenticated user",
        responses={
            status.HTTP_200_OK: UserSerializer,
        }
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="Change the password for a user account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password'],
            properties={
                'old_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Current password"
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New password"
                )
            }
        ),
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description='No content'),
        }
    )
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {"detail": "Invalid old password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamViewSet(viewsets.ModelViewSet):
    """Manage manufacturing teams."""
    
    queryset = Team.objects.prefetch_related(
        'members',
        'members__user'
    ).all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = TeamFilter
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Team.objects.none()
        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="List teams",
        operation_description="Get a paginated list of all teams",
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description=f"Filter by team type ({', '.join(TeamTypes().__dict__.values())})",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Filter by team name (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'created_at_after',
                openapi.IN_QUERY,
                description="Filter teams created after this date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'created_at_before',
                openapi.IN_QUERY,
                description="Filter teams created before this date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order by field. Use '-' prefix for descending order (e.g. -created_at, name)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create team",
        operation_description="Create a new team with specified type and name",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['type', 'name'],
            properties={
                'type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Team type (WING, BODY, TAIL, AVIONICS)"
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Team name"
                )
            }
        ),
        responses={
            201: TeamSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get team details",
        operation_description="Get detailed information about a specific team",
        responses={
            status.HTTP_200_OK: TeamSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update team",
        operation_description="Update team information",
        responses={
            status.HTTP_200_OK: TeamSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update team",
        operation_description="Update specific fields of team information",
        responses={
            status.HTTP_200_OK: TeamSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete team",
        operation_description="Delete a team. Only empty teams can be deleted.",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description='No content'),
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        if team.members.exists():
            return Response(
                {"detail": "Cannot delete team with members"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class TeamTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for managing team types."""
    queryset = TeamType.objects.all()
    serializer_class = TeamTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = TeamTypeFilter
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: TeamTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamTypeSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description='No content'),
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TeamMemberViewSet(viewsets.ModelViewSet):
    """Manage team member assignments."""
    
    serializer_class = TeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = TeamMemberFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    queryset = TeamMember.objects.select_related(
        'user',
        'team'
    ).all()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TeamMember.objects.none()
        return super().get_queryset()

    @swagger_auto_schema(
        operation_summary="List team members",
        operation_description="Get a paginated list of all team members",
        manual_parameters=[
            openapi.Parameter(
                'team',
                openapi.IN_QUERY,
                description="Filter by team ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'team_type',
                openapi.IN_QUERY,
                description=f"Filter by team type ({', '.join(TeamTypes().__dict__.values())})",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'user_email',
                openapi.IN_QUERY,
                description="Filter by user email (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'user_username',
                openapi.IN_QUERY,
                description="Filter by username (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order by field. Use '-' prefix for descending order (e.g. -created_at)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get team member details",
        operation_description="Get detailed information about a specific team member",
        responses={
            status.HTTP_200_OK: TeamMemberSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create team member",
        operation_description="Add a user to a team",
        responses={
            201: TeamMemberSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update team member",
        operation_description="Update team member information",
        responses={
            status.HTTP_200_OK: TeamMemberSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


    @swagger_auto_schema(
        operation_summary="Partially update team member",
        operation_description="Update specific fields of team member information",
        responses={
            status.HTTP_200_OK: TeamMemberSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Remove team member",
        operation_description="Remove a user from their team",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description='No content'),
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
