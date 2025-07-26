from rest_framework import serializers
from .models import Project, Task, Skill, Resources

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    skill_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        write_only=True,
        source='skills'
    )
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'name', 'start_date', 'end_date', 'project', 'skill_id', 'skills']


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


