from rest_framework.routers import DefaultRouter
from . import views

app_name = 'assembly'
router = DefaultRouter()
router.register('aircraft', views.AircraftViewSet, basename='aircraft')
# router.register('aircraft-types', views.AircraftTypeViewSet, basename='aircraft-type')

urlpatterns = router.urls