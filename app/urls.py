from rest_framework.routers import DefaultRouter
from .views import  (ProjectViewSet, TaskViewSet, ResourcesViewSet, SkillViewSet,
                     getAvailability, AssignmentViewSet )
from django.urls import include, path
router = DefaultRouter()

router.register('resources', ResourcesViewSet, basename='resources')
router.register('projects', ProjectViewSet, basename='projects')
router.register('tasks', TaskViewSet, basename='tasks')
router.register('skills', SkillViewSet, basename='skills')
router.register('assign', AssignmentViewSet, basename='assign')

urlpatterns = [
    path('search', getAvailability, name='search'),
]
urlpatterns += router.urls
