from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'
router = DefaultRouter()
router.register('parts', views.PartViewSet, basename='parts')
# router.register('part-types', views.PartTypeViewSet, basename='part-type')
# router.register('team-part-permissions', views.TeamPartPermissionViewSet, basename='team-part-permission')

urlpatterns = router.urls
