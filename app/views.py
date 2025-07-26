from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from django.db.models import Q, Count
from .models import Project, Task, Skill, Resources
from .serializer import ProjectSerializer, TaskSerializer, SkillSerializer, ResourcesSerializer

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.prefetch_related('skills').all()
    serializer_class = TaskSerializer


class SkillViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ResourcesViewSet(ModelViewSet):
    queryset = Resources.objects.prefetch_related('skills').all()
    serializer_class = ResourcesSerializer

@api_view(['GET'])
def getAvailability(request):
    task_id = request.GET.get('task')
    task = get_object_or_404(Task, id=task_id)

    required_skills = task.skills.all()

    if task.start_date and task.end_date:
        # find at least one skill matching
        # resources availability dates is earlier
        # or equal to the task starting & ending dates
        persons = Resources.objects.filter(
            available_start_date__lte=task.start_date,
            available_end_date__gte=task.end_date,
            skills__in=required_skills
        ).annotate(
            skill_match_count=Count('skills')
        ).distinct()

        if(persons.exists()):
            person_list = []
            for p in persons:
                person_list.append({
                    "name": p.name,
                    "skills": [s.name for s in p.skills.all()],
                    "available_start_date": p.available_start_date.strftime("%d-%m-%Y"),
                    "available_end_date": p.available_end_date.strftime("%d-%m-%Y"),
                    "matching_skills_count": p.skill_match_count,
                })

            return Response({
                'task': {
                    "name": task.name,
                    "start_date": task.start_date.strftime("%d-%m-%Y"),
                    "end_date": task.end_date.strftime("%d-%m-%Y"),
                    "skills": [s.name for s in task.skills.all()],
                },
                "resources_count": len(person_list),
                "available_resources": person_list
            }, status=HTTP_200_OK)
        else:
            return Response({
                'task': {
                    "name": task.name,
                    "start_date": task.start_date.strftime("%d-%m-%Y"),
                    "end_date": task.end_date.strftime("%d-%m-%Y"),
                    "skills": [s.name for s in task.skills.all()],
                },
                "resources_count": 0,
                "available_resources": "No resources are available"
            }, status=HTTP_200_OK)

    return Response({"message": "Task has no valid start/end date."}, status=HTTP_404_NOT_FOUND)