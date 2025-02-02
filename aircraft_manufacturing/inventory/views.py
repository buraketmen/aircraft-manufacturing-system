from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.permissions import IsMemberOfTeam, IsSuperUserOrReadOnly
from aircraft_manufacturing.responses import GeneralFailedResponseSerializer
from aircraft_manufacturing.pagination import DataTablePagination
from inventory.models import Part, PartType, TeamPartPermission
from inventory.serializers import PartSerializer, PartTypeSerializer, TeamPartPermissionSerializer
from inventory.filters import PartFilter, PartTypeFilter, TeamPartPermissionFilter
from .models import PartType
from rest_framework.exceptions import MethodNotAllowed

class PartTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for managing part types."""
    queryset = PartType.objects.all()
    serializer_class = PartTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = PartTypeFilter
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PartTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: PartTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PartTypeSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PartTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: PartTypeSerializer,
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


class TeamPartPermissionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing team part permissions."""
    queryset = TeamPartPermission.objects.select_related(
        'team_type',
        'part_type'
    ).all()
    serializer_class = TeamPartPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = TeamPartPermissionFilter
    ordering_fields = ['team_type__name', 'part_type__name', 'created_at']
    ordering = ['team_type__name', 'part_type__name']

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamPartPermissionSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: TeamPartPermissionSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamPartPermissionSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamPartPermissionSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TeamPartPermissionSerializer,
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


class PartViewSet(viewsets.ModelViewSet):
    """API endpoint for managing parts."""
    queryset = Part.objects.select_related(
        'part_type',
        'aircraft_type',
        'owner',
        'owner__user',
        'owner__team',
        'owner__team__team_type'
    ).all()
    serializer_class = PartSerializer
    permission_classes = [permissions.IsAuthenticated, IsMemberOfTeam]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = PartFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    http_method_names = ['head', 'get', 'post', 'delete']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Part.objects.none()
        return self.queryset

    @swagger_auto_schema(
        operation_summary="List parts",
        operation_description="Get a paginated list of all parts",
        manual_parameters=[
            openapi.Parameter(
                'part_type',
                openapi.IN_QUERY,
                description="Filter by part type",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'aircraft_type',
                openapi.IN_QUERY,
                description="Filter by aircraft type",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'is_used',
                openapi.IN_QUERY,
                description="Filter by usage status",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
        ],
        responses={
            status.HTTP_200_OK: PartSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create part",
        operation_description="Create a new part",
        request_body=PartSerializer,
        responses={
            status.HTTP_201_CREATED: PartSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        # Set owner to current team member
        team_member = getattr(request.user, 'teammember', None)
        if not team_member:
            return Response(
                {"detail": "You are not a member of any team"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create part
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=team_member)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Get part details",
        operation_description="Get details of a specific part",
        responses={
            status.HTTP_200_OK: PartSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update part",
        operation_description="Update a specific part",
        request_body=PartSerializer,
        responses={
            status.HTTP_200_OK: PartSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        },
        deprecated=True
    )
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT method is not allowed")

    @swagger_auto_schema(
        operation_summary="Partial update part",
        operation_description="Partially update a specific part",
        request_body=PartSerializer,
        responses={
            status.HTTP_200_OK: PartSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        },
        deprecated=True
    )
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH method is not allowed")

    @swagger_auto_schema(
        operation_summary="Delete part",
        operation_description="Delete a specific part",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description='No content'),
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_summary="Get part requirements",
        operation_description="Get the required parts for each aircraft type",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'aircraft_type': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'part_type': openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                )
                            }
                        )
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], pagination_class=None, filterset_class=None)
    def requirements(self, *args, **kwargs):
        """Get the required parts for each aircraft type."""
        from assembly.models import AircraftType, AircraftPartRequirement

        result = {}
        aircraft_types = AircraftType.objects.all()

        for aircraft_type in aircraft_types:
            # Get required parts
            required_parts = {
                req.part_type.name: req.quantity
                for req in AircraftPartRequirement.objects.filter(aircraft_type=aircraft_type)
            }
            result[aircraft_type.name] = required_parts

        return Response(result)

    @swagger_auto_schema(
        operation_summary="List parts",
        operation_description="Get a paginated list of all parts",
        manual_parameters=[
            openapi.Parameter(
                'is_used',
                openapi.IN_QUERY,
                description="Filter by part usage status",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Filter by part type (WING, BODY, TAIL, AVIONICS)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'aircraft_type',
                openapi.IN_QUERY,
                description="Filter by aircraft type (TB2, AKINCI)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'owner_name',
                openapi.IN_QUERY,
                description="Filter by creator's username",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'created_at_after',
                openapi.IN_QUERY,
                description="Filter parts created after this date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'created_at_before',
                openapi.IN_QUERY,
                description="Filter parts created before this date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
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
        operation_summary="Retrieve part details",
        operation_description="Get details of a specific part",
        responses={200: PartSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        

    @swagger_auto_schema(
        operation_summary="Create new part",
        operation_description="Create a new part. Part type must match creator's team type.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['type', 'aircraft_type'],
            properties={
                'type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Part type (must match creator's team type)"
                ),
                'aircraft_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Aircraft type this part is for"
                )
            }
        ),
        responses={
            201: PartSerializer,
            400: GeneralFailedResponseSerializer,
            403: GeneralFailedResponseSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Create a new part."""
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=self.request.user.teammember)


    @swagger_auto_schema(
        operation_summary="Update part",
        operation_description="Update an existing part. Only the team that created the part can update it.",
        responses={
            200: PartSerializer,
            400: GeneralFailedResponseSerializer,
            403: GeneralFailedResponseSerializer
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=self.request.user.teammember)
    
    @swagger_auto_schema(
        operation_summary="Partial update part",
        operation_description="Update an existing part. Only the team that created the part can update it.",
        responses={
            200: PartSerializer,
            400: GeneralFailedResponseSerializer,
            403: GeneralFailedResponseSerializer
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_partial_update(self, serializer):
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(owner=self.request.user.teammember)

    @swagger_auto_schema(
        operation_summary="Recycle part",
        operation_description="Recycle (delete) an unused part. Only the team that created the part can recycle it.",
        responses={
            204: "No content",
            400: GeneralFailedResponseSerializer,
            403: GeneralFailedResponseSerializer
        }
    )
    def destroy(self, request, *args, **kwargs):
        part = self.get_object()
        if part.is_used:
            return Response(
                {"detail": "Cannot recycle a part that is used in an aircraft"},
                status=400
            )
        if part.owner.team != request.user.teammember.team:
            return Response(
                {"detail": "You can only recycle parts produced by your team"},
                status=403
            )
        part.delete()
        return Response(status=204)

    @swagger_auto_schema(
        operation_summary="Get inventory status",
        operation_description="Get current inventory status for all part types",
        manual_parameters=None,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additionalProperties=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'available': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'used': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='inventory-status', pagination_class=None, filterset_class=None)
    def inventory_status(self, request, *args, **kwargs):
        """Get inventory status for each aircraft type"""
        from assembly.models import AircraftType, AircraftPartRequirement


        inventory = {}
        aircraft_types = AircraftType.objects.all()
        
        # Process each aircraft type
        for aircraft_type in aircraft_types:
            parts_status = {}
            
            # For each part type, count parts for this aircraft type
            for instance in AircraftPartRequirement.objects.select_related('part_type').only('part_type').filter(aircraft_type=aircraft_type):
                part_type = getattr(instance, 'part_type', None)
                    
                if not part_type:
                    continue
                    
                parts = Part.objects.filter(
                    aircraft_type=aircraft_type,
                    part_type=part_type
                )
                total = parts.count()
                used = parts.filter(is_used=True).count()
                
                parts_status[part_type.name] = {
                    'total': total,
                    'available': total - used,
                    'used': used
                }
            
            inventory[aircraft_type.name] = parts_status
        
        return Response(data=inventory)

    @swagger_auto_schema(
        operation_summary="Get available parts",
        operation_description="Get list of available parts for a specific aircraft type",
        manual_parameters=[
            openapi.Parameter(
                'aircraft_type',
                openapi.IN_PATH,
                description="Aircraft type to check parts for",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'can_assemble': openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Whether all required parts are available"
                    ),
                    "missing_parts": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'type': openapi.Schema(type=openapi.TYPE_STRING),
                                'required': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'available': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        )
                    ),
                    'required_parts': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additionalProperties=openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        )
                    ),
                    'parts': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'type': openapi.Schema(type=openapi.TYPE_STRING),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                               
                            }
                        )
                    ),
                    'detail': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Status message"
                    ),
                    
                    
                }
            ),
            400: GeneralFailedResponseSerializer
        }
    )
    @action(detail=False, methods=['get'], url_path='available/(?P<aircraft_id>[^/.]+)')
    def available_parts(self, request, *args, **kwargs):
        """Get available parts for a specific aircraft type."""
        from assembly.models import AircraftType, AircraftPartRequirement

        # Get aircraft type from database
        aircraft_type_id = kwargs.get('aircraft_id')
        try:
            aircraft_type = AircraftType.objects.get(id=aircraft_type_id)
        except (ValueError, AircraftType.DoesNotExist):
            return Response(
                {"detail": f"Invalid aircraft type: {aircraft_type_id}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get required parts from database
        required_parts = {
            req.part_type.name: req.quantity
            for req in AircraftPartRequirement.objects.filter(aircraft_type=aircraft_type)
        }
        if not required_parts:
            return Response(
                {"detail": f"No required parts defined for aircraft type: {aircraft_type.name}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get available parts
        available_parts = Part.objects.filter(
            aircraft_type=aircraft_type,
            is_used=False
        ).select_related('part_type').order_by('part_type__name', 'created_at')

        # Get available parts count for each type
        parts_count = available_parts.values('part_type__name').annotate(
            count=Count('id')
        ).order_by('part_type__name')

        # Check if we have all required parts
        can_assemble = True
        missing_parts = []

        for part_type, required_count in required_parts.items():
            available_count = next(
                (item['count'] for item in parts_count if item['part_type__name'] == part_type),
                0
            )
            if available_count < required_count:
                can_assemble = False
                missing_parts.append({
                    'type': part_type,
                    'required': required_count,
                    'available': available_count
                })

        # Prepare parts list for frontend
        parts = []
        if can_assemble:
            parts = [
                {
                    'id': part.id,
                    'type': part.part_type.name,
                    'created_at': part.created_at
                }
                for part in available_parts
            ]

        return Response({
            'can_assemble': can_assemble,
            'missing_parts': missing_parts,
            'required_parts': required_parts,
            'parts': parts,
            'detail': "All required parts are available" if can_assemble else None
        })
