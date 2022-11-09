from rest_framework import viewsets, generics

from .serializers import ProblemSerializer
from .models import Problem
from rest_framework.decorators import action, api_view
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from .solver import solver


@api_view(["GET", "POST", "DELETE"])
def problem_list(request):
    if request.method == "GET":
        problems = Problem.objects.all()
        problems_serializer = ProblemSerializer(problems, many=True)
        return JsonResponse(problems_serializer.data, safe=False)
    elif request.method == "POST":
        problem_data = JSONParser().parse(request)
        problem_serializer = ProblemSerializer(data=problem_data)
        if problem_serializer.is_valid():
            problem_serializer.save()
            return JsonResponse(problem_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            problem_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET", "PUT", "DELETE"])
def problem_detail(request, pk):
    try:
        problem = Problem.objects.get(pk=pk)
        problem_serializer = ProblemSerializer(problem)
        return JsonResponse(problem_serializer.data)
    except Problem.DoesNotExist:
        return JsonResponse(
            {"message": "The problem does not exist"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def problem_solve(request, pk):
    try:
        problem = Problem.objects.get(pk=pk)
        print(problem)

    except Problem.DoesNotExist:
        return JsonResponse(
            {"message": "The problem does not exist"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST", "OPTIONS"])
def solve(request):
    if request.method == "OPTIONS":
        print(request)
        return JsonResponse({"message": "OK"})
    else:
        try:
            problem_data = JSONParser().parse(request)
            solution = solver.solve_linear_program(
                problem_data["variableCells"],
                problem_data["constraints"],
                problem_data["objectiveTarget"],
                problem_data["objectiveFormula"],
            )
            return JsonResponse(
                solution,
                status=status.HTTP_200_OK,
            )
        except Problem.DoesNotExist:
            return JsonResponse(
                {"message": "The problem does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def problem_list_published(request):
    pass
