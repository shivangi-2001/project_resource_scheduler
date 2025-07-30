from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.db.models import Q, Count
from .models import Project, Task, Skill, Resources, Assignment
from .serializer import ProjectSerializer, TaskSerializer, SkillSerializer, ResourcesSerializer, AssignmentSerializer

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

class AssignmentViewSet(ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer


@api_view(['GET'])
def getAvailability(request):
    task_id = request.GET.get('task')
    task = get_object_or_404(Task, id=task_id)

    if not (task.start_date and task.end_date):
        return Response({"message": "Task has no valid start/end date."}, status=HTTP_400_BAD_REQUEST)

    # 1. Required skills for the task
    required_skills = set(task.skills.values_list('name', flat=True))

    # 2. Already assigned resources
    assigned_resources = task.assignments.values_list('resource', flat=True)

    # 3. Determine remaining skills
    if not assigned_resources:
        remaining_skills = required_skills
    else:
        assigned_skills = Skill.objects.filter(
            assignments__task=task
        ).values_list('name', flat=True)
        remaining_skills = required_skills - set(assigned_skills)

    # 4. Search available resources that match remaining skills
    available_resources = Resources.objects.exclude(
        id__in=assigned_resources
    ).filter(
        available_start_date__lte=task.start_date,
        available_end_date__gte=task.end_date,
        skills__name__in=remaining_skills
    ).annotate(
        matching_count=Count('skills', filter=Q(skills__name__in=remaining_skills))
    ).distinct().order_by('-matching_count')

    # 5. Prepare response list
    person_list = []
    for p in available_resources:
        resource_skills = set(p.skills.values_list('name', flat=True))
        matching_skills = resource_skills & remaining_skills

        person_list.append({
            "id": p.id,
            "name": p.name,
            "skills": list(resource_skills),
            "available_start_date": p.available_start_date.strftime("%d-%m-%Y"),
            "available_end_date": p.available_end_date.strftime("%d-%m-%Y"),
            "matching_skills_count": len(matching_skills),
            "matching_skills": list(matching_skills),
        })

    # 6. Return full task + resource match info
    return Response({
        'task': {
            "name": task.name,
            "start_date": task.start_date.strftime("%d-%m-%Y"),
            "end_date": task.end_date.strftime("%d-%m-%Y"),
            "required_skills": list(required_skills),
            "remaining_skills": list(remaining_skills),
            "assigned_resources": list(task.assignments.values('resource__name', 'max_skill_covered'))
        },
        "resources_count": len(person_list),
        "available_resources": person_list or "No resources available"
    }, status=HTTP_200_OK)

