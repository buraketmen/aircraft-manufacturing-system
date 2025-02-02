from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from accounts.views import HomeView, CustomLoginView
from django.contrib.auth.views import LogoutView

from django.conf.urls.static import static

# Create schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Aircraft Manufacturing API",
        default_version='v1',
        description="API for managing aircraft manufacturing process",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path('', include('aircraft_manufacturing.urls'))],
)


urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    # Frontend
    path('', HomeView.as_view(), name='home'),
    # Auth
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout', kwargs={'method': ['GET', 'POST']}),
    # API
    path(
        "api/",
        include(
            [
                re_path(
                    r"^(?P<version>(v1))/",
                    include(
                        [
                            path('accounts/', include('accounts.urls')),
                            path('inventory/', include('inventory.urls')),
                            path('assembly/', include('assembly.urls')),
                            path('auth/', include('rest_framework.urls')),
                        ]
                    ),
                ),
            ]
        )
    ),
    # Documentation
    re_path(r"^api/$", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r"^docs/$", schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
