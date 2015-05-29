"""
View methods for the course team feature.
"""

from django.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_with_access
from django.http import Http404
from django.conf import settings


def teams_dashboard(request, course_id):
    """
    Renders the teams dashboard, which is shown on the "Teams" tab.
    """
    # TODO: add unit tests for these conditions
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)

    if not is_feature_enabled(course):
        raise Http404

    context = {
        "course": course,
    }

    return render_to_response("teams/teams.html", context)


def is_feature_enabled(course):
    """
    Returns True if the teams feature is enabled.
    """
    return settings.FEATURES.get('ENABLE_TEAMS', False) and course.teams_enabled
