from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('teams', views.TeamViewSet, basename='teams')
# router.register('team-members', views.TeamMemberViewSet, basename='team-member')
# router.register('team-types', views.TeamTypeViewSet, basename='team-type')

urlpatterns = router.urls