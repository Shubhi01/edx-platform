"""
Definition of the course team feature.
"""

from django.conf import settings
from django.utils.translation import ugettext as _
from courseware.tabs import EnrolledCourseViewType


class TeamsCourseViewType(EnrolledCourseViewType):
    """
    The representation of the course teams view type.
    """

    name = "teams"
    title = _("Teams")
    view_name = "teams_dashboard"

    @classmethod
    def is_enabled(cls, course, user=None):  # pylint: disable=unused-argument
        """Returns true if the teams feature is enabled in the course.

        Args:
            course (CourseDescriptor): the course using the feature
            settings (dict): a dict of configuration settings
            user (User): the user interacting with the course
        """
        if not super(TeamsCourseViewType, cls).is_enabled(course, user=user):
            return False

        return settings.FEATURES.get('ENABLE_TEAMS', False) and course.teams_enabled
