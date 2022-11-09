from django.db import models


class Problem(models.Model):
    name = models.CharField(max_length=100)
    objective = models.TextField()
    objectiveGoal = models.CharField(max_length=10)
    objectiveValue = models.FloatField()
    variableCells = models.TextField()
    constraints = models.TextField()

    def __str__(self):
        return self.name
