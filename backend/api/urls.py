from django.urls import include, re_path, path
from rest_framework import routers
from . import views


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(
        r"^api/problems/(?P<pk>[0-9]+)$",
        views.problem_detail,
        name="problem-detail",
    ),
    re_path(
        r"^api/problems/(?P<pk>[0-9]+)/solve$",
        views.problem_solve,
        name="problem-detail",
    ),
    re_path(
        r"^api/solve$",
        views.solve,
        name="solve",
    ),
    re_path(
        r"^api/problems$",
        views.problem_list,
        name="problem-list",
    ),
]
