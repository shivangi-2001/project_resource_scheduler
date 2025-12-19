from rest_framework import serializers
from .models import Project, Task, Skill, Resources, Assignment


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class AssignedSerializer(serializers.ModelSerializer):


    class Meta:
        model = Assignment
        fields = ['resource', 'max_skill_covered']


class TaskSerializer(serializers.ModelSerializer):
    skill_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        source='skills'
    )
    skills = serializers.SerializerMethodField()
    list_of_resources = AssignedSerializer(many=True, source='assignments', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'start_date', 'end_date', 'project', 'skill_id', 'skills', 'list_of_resources']


    def get_skills(self, obj):
        return [skill.name for skill in obj.skills.all()]

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and start > end:
            raise serializers.ValidationError("Start date must not be later than end date.")
        return data


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'tasks']


class ResourcesSerializer(serializers.ModelSerializer):
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        source='skills'
    )
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Resources
        fields = ['id', 'name', 'available_start_date', 'available_end_date', 'skill_ids', 'skills']

    def get_skills(self, obj):
        return [skill.name for skill in obj.skills.all()]

    def validate(self, data):
        start = data.get('available_start_date')
        end = data.get('available_end_date')
        if start and end and start > end:
            raise serializers.ValidationError("Available start date must not be later than end date.")
        return data


class AssignmentSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'task', 'resource', 'skills', 'assigned_at', 'max_skill_covered']
        read_only_fields = ['assigned_at', 'max_skill_covered']

    def get_skills(self, obj):
        return [skill.name for skill in obj.matching_skills.all()]

    def create(self, validated_data):
        task = validated_data['task']
        resource = validated_data['resource']

        # check availability of resources with task
        if not (resource.available_start_date <= task.start_date and resource.available_end_date >= task.end_date):
            raise serializers.ValidationError("Resource is not available for the entire duration of the task.")

        # Get skills
        task_skills = set(task.skills.all())
        resource_skills = set(resource.skills.all())
        matching_skills = task_skills & resource_skills

        if len(matching_skills) == 0:
            raise serializers.ValidationError("No matching skills found.")

        # Calculate percentage of matching skills
        if task_skills:
            max_skill_covered = round(len(matching_skills) / len(task_skills), 2)
        else:
            max_skill_covered = 0.0

        # Create assignment
        assignment = Assignment.objects.create(
            task=task,
            resource=resource,
            max_skill_covered=max_skill_covered
        )
        assignment.matching_skills.set(matching_skills)
        return assignment
