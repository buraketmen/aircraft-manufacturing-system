from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django.db.models import Prefetch, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.permissions import IsMemberOfAssemblyTeam, IsSuperUserOrReadOnly
from aircraft_manufacturing.responses import GeneralFailedResponseSerializer
from .models import Aircraft, AircraftType, AircraftPart, AircraftPartRequirement
from .serializers import AircraftSerializer, AircraftTypeSerializer
from inventory.serializers import PartSerializer
from inventory.models import Part
from aircraft_manufacturing.pagination import DataTablePagination
from .filters import AircraftFilter, AircraftTypeFilter
from django.db import transaction
from rest_framework.exceptions import MethodNotAllowed


class AircraftTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for managing aircraft types."""
    queryset = AircraftType.objects.all()
    serializer_class = AircraftTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrReadOnly]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = AircraftTypeFilter
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: AircraftTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: AircraftTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: AircraftTypeSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: AircraftTypeSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: AircraftTypeSerializer,
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


class AircraftViewSet(viewsets.ModelViewSet):
    """Manage aircraft assembly operations."""
    serializer_class = AircraftSerializer
    permission_classes = [permissions.IsAuthenticated, IsMemberOfAssemblyTeam]
    pagination_class = DataTablePagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = AircraftFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    http_method_names = ['head', 'get', 'post', 'delete']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Aircraft.objects.none()

        return Aircraft.objects.select_related(
            'aircraft_type',
        ).prefetch_related(
            Prefetch(
                'used_parts',
                queryset=AircraftPart.objects.select_related(
                    'part',
                    'part__part_type',
                    'part__aircraft_type',
                    'part__owner',
                    'part__owner__user',
                    'part__owner__team',
                    'part__owner__team__team_type'
                )
            )
        ).all()

    @swagger_auto_schema(
        operation_summary="List assembled aircraft",
        operation_description="Get a paginated list of all assembled aircraft",
        manual_parameters=[
            openapi.Parameter(
                'aircraft_type',
                openapi.IN_QUERY,
                description="Filter by aircraft type",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'assembled_after',
                openapi.IN_QUERY,
                description="Filter aircraft assembled after this date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
            openapi.Parameter(
                'assembled_before',
                openapi.IN_QUERY,
                description="Filter aircraft assembled before this date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False
            ),
        ],
        responses={
            status.HTTP_200_OK: AircraftSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create aircraft",
        operation_description="Create a new aircraft",
        request_body=AircraftSerializer,
        responses={
            status.HTTP_201_CREATED: AircraftSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
        }
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Set assembly team to current team member's team
        team_member = getattr(request.user, 'teammember', None)
        if not team_member:
            return Response(
                {"detail": "You are not a member of any team"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create aircraft
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save aircraft with assembly team
        aircraft = serializer.save()
                
        # Collect all part IDs
        part_ids = []
        aircraft_parts = []
        parts_data = request.data.get('parts', {})
        
        for part_type, type_part_ids in parts_data.items():
            if not type_part_ids:
                continue
            # Remove _ids suffix to get part type name
            part_type = part_type.replace('_ids', '')  
            for part_id in type_part_ids:
                part_ids.append(part_id)
                aircraft_parts.append(
                    AircraftPart(
                        aircraft=aircraft,
                        part_id=part_id
                    )
                )
        
        if part_ids:
            AircraftPart.objects.bulk_create(aircraft_parts)
            Part.objects.filter(id__in=part_ids).update(is_used=True)

        serializer = self.get_serializer(aircraft)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Get aircraft details",
        operation_description="Get details of a specific aircraft",
        responses={
            status.HTTP_200_OK: AircraftSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update aircraft",
        operation_description="Update a specific aircraft",
        request_body=AircraftSerializer,
        responses={
            status.HTTP_200_OK: AircraftSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        },
        deprecated=True
    )
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT method is not allowed")

    @swagger_auto_schema(
        operation_summary="Partial update aircraft",
        operation_description="Partially update a specific aircraft",
        request_body=AircraftSerializer,
        responses={
            status.HTTP_200_OK: AircraftSerializer,
            status.HTTP_400_BAD_REQUEST: GeneralFailedResponseSerializer,
            status.HTTP_404_NOT_FOUND: GeneralFailedResponseSerializer,
        },
        deprecated=True
    )
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH method is not allowed")

    @swagger_auto_schema(
        operation_summary="Delete aircraft",
        operation_description="Delete a specific aircraft",
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
                    additionalProperties=openapi.Schema(  # Dinamik key-value desteği
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "can_assemble": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "missing_parts": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "type": openapi.Schema(type=openapi.TYPE_STRING),
                                        "required": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "available": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    },
                                ),
                            ),
                            "required_parts": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                additionalProperties=openapi.Schema(type=openapi.TYPE_INTEGER),
                            ),
                            "parts": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_OBJECT),
                            ),
                            "detail": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
        }
    )
    @action(detail=False, methods=['get'], url_path='requirements', pagination_class=None, filterset_class=None)
    def requirements(self, *args, **kwargs):
        """Get the required parts for each aircraft type."""
        def get_required_parts(aircraft_type):
            """Get required parts for aircraft type"""        
            # Get required parts from database
            required_parts = {
                req.part_type.name: req.quantity
                for req in AircraftPartRequirement.objects.filter(aircraft_type=aircraft_type)
            }
            
            # Get available parts
            available_parts = Part.objects.filter(
                aircraft_type=aircraft_type,
                is_used=False
            ).select_related('part_type').values('part_type__name').annotate(count=Count('id'))
            
            available_parts_dict = {
                part['part_type__name']: part['count']
                for part in available_parts
            }
            
            # Check if all required parts are available
            missing_parts = [
                {'type': part_type, 'required': required_count, 'available': available_parts_dict.get(part_type, 0)}
                for part_type, required_count in required_parts.items()
                if available_parts_dict.get(part_type, 0) < required_count
            ]
            
            # Get all available parts for this aircraft type
            parts = Part.objects.filter(
                aircraft_type=aircraft_type,
                is_used=False
            ).select_related('part_type').order_by('part_type__name', 'created_at')
            
            return {
                'can_assemble': len(missing_parts) == 0,
                'missing_parts': missing_parts,
                'required_parts': required_parts,
                'parts': PartSerializer(parts, many=True).data,
                'detail': None
            }
        requirements = {}
        for aircraft_type in AircraftType.objects.all():
            requirements[aircraft_type.name] = get_required_parts(aircraft_type=aircraft_type)
        return Response(data=requirements)