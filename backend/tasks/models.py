from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(default=0)
    importance = models.IntegerField(default=5)  # 1-10
    dependencies = models.JSONField(default=list)  # list of task IDs
