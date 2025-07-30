from django.db import models

class Project(models.Model):
    title = models.CharField(unique=True, max_length=100, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Skill(models.Model):
    name = models.CharField(unique=True, max_length=1000)

    def __str__(self):
        return self.name

class Resources(models.Model):
    name = models.CharField(max_length=100)
    skills = models.ManyToManyField(Skill, related_name='resources')
    available_start_date = models.DateField()
    available_end_date = models.DateField()

    def __str__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(unique=True, max_length=100)
    skills = models.ManyToManyField(Skill, related_name='skills')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name}"

class Assignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE, related_name='assignments')
    max_skill_covered = models.FloatField(default=0.0)
    matching_skills = models.ManyToManyField(Skill, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'resource')

    def __str__(self):
        return f"{self.resource.name} assigned to {self.task.name}"







