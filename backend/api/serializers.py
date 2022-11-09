from rest_framework import serializers
from .models import Problem


class ProblemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Problem
        fields = [
            "name",
            "objective",
            "objectiveGoal",
            "objectiveValue",
            "variableCells",
            "constraints",
        ]
