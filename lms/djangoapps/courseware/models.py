"""
WE'RE USING MIGRATIONS!

If you make changes to this model, be sure to create an appropriate migration
file and check it in at the same time as your model changes. To do that,

1. Go to the edx-platform dir
2. ./manage.py schemamigration courseware --auto description_of_your_change
3. Add the migration file created in edx-platform/lms/djangoapps/courseware/migrations/


ASSUMPTIONS: modules have unique IDs, even across different module_types

"""
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import pymongo.collection
import pymongo.connection


class StudentModule(models.Model):
    """
    Keeps student state for a particular module in a particular course.
    """
    # For a homework problem, contains a JSON
    # object consisting of state
    MODULE_TYPES = (('problem', 'problem'),
                    ('video', 'video'),
                    ('html', 'html'),
                    ('timelimit', 'timelimit'),
                    )
    ## These three are the key for the object
    module_type = models.CharField(max_length=32, choices=MODULE_TYPES, default='problem', db_index=True)

    # Key used to share state. By default, this is the module_id,
    # but for abtests and the like, this can be set to a shared value
    # for many instances of the module.
    # Filename for homeworks, etc.
    module_state_key = models.CharField(max_length=255, db_index=True, db_column='module_id')
    # student = models.ForeignKey(User, db_index=True)
    student_id = models.IntegerField(db_index=True)
    course_id = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = (('student_id', 'module_state_key', 'course_id'),)

    ## Internal state of the object
    state = models.TextField(null=True, blank=True)

    ## Grade, and are we done?
    grade = models.FloatField(null=True, blank=True, db_index=True)
    max_grade = models.FloatField(null=True, blank=True)
    DONE_TYPES = (('na', 'NOT_APPLICABLE'),
                    ('f', 'FINISHED'),
                    ('i', 'INCOMPLETE'),
                    )
    done = models.CharField(max_length=8, choices=DONE_TYPES, default='na', db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    def __repr__(self):
        return 'StudentModule<%r>' % ({
            'course_id': self.course_id,
            'module_type': self.module_type,
            'student': self.student.username,
            'module_state_key': self.module_state_key,
            'state': str(self.state)[:20],
        },)

    def __unicode__(self):
        return unicode(repr(self))


class StudentModuleHistory(models.Model):
    """Keeps a complete history of state changes for a given XModule for a given
    Student. Right now, we restrict this to problems so that the table doesn't
    explode in size."""

    HISTORY_SAVING_TYPES = {'problem'}

    class Meta:
        get_latest_by = "created"

    student_module = models.ForeignKey(StudentModule, db_index=True)
    version = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # This should be populated from the modified field in StudentModule
    created = models.DateTimeField(db_index=True)
    state = models.TextField(null=True, blank=True)
    grade = models.FloatField(null=True, blank=True)
    max_grade = models.FloatField(null=True, blank=True)

    @receiver(post_save, sender=StudentModule)
    def save_history(sender, instance, **kwargs):
        if instance.module_type in StudentModuleHistory.HISTORY_SAVING_TYPES:
            history_entry = StudentModuleHistory(student_module=instance,
                                                 version=None,
                                                 created=instance.modified,
                                                 state=instance.state,
                                                 grade=instance.grade,
                                                 max_grade=instance.max_grade)
            history_entry.save()


class XModuleUserStateSummaryField(models.Model):
    """
    Stores data set in the Scope.user_state_summary scope by an xmodule field
    """

    class Meta:
        unique_together = (('usage_id', 'field_name'),)

    # The name of the field
    field_name = models.CharField(max_length=64, db_index=True)

    # The definition id for the module
    usage_id = models.CharField(max_length=255, db_index=True)

    # The value of the field. Defaults to None dumped as json
    value = models.TextField(default='null')

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    def __repr__(self):
        return 'XModuleUserStateSummaryField<%r>' % ({
            'field_name': self.field_name,
            'usage_id': self.usage_id,
            'value': self.value,
        },)

    def __unicode__(self):
        return unicode(repr(self))


class XModuleStudentPrefsField(models.Model):
    """
    Stores data set in the Scope.preferences scope by an xmodule field
    """

    class Meta:
        unique_together = (('student', 'module_type', 'field_name'),)

    # The name of the field
    field_name = models.CharField(max_length=64, db_index=True)

    # The type of the module for these preferences
    module_type = models.CharField(max_length=64, db_index=True)

    # The value of the field. Defaults to None dumped as json
    value = models.TextField(default='null')

    student = models.ForeignKey(User, db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    def __repr__(self):
        return 'XModuleStudentPrefsField<%r>' % ({
            'field_name': self.field_name,
            'module_type': self.module_type,
            'student': self.student.username,
            'value': self.value,
        },)

    def __unicode__(self):
        return unicode(repr(self))


class XModuleStudentInfoField(models.Model):
    """
    Stores data set in the Scope.preferences scope by an xmodule field
    """

    class Meta:
        unique_together = (('student', 'field_name'),)

    # The name of the field
    field_name = models.CharField(max_length=64, db_index=True)

    # The value of the field. Defaults to None dumped as json
    value = models.TextField(default='null')

    student = models.ForeignKey(User, db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    def __repr__(self):
        return 'XModuleStudentInfoField<%r>' % ({
            'field_name': self.field_name,
            'student': self.student.username,
            'value': self.value,
        },)

    def __unicode__(self):
        return unicode(repr(self))


class OfflineComputedGrade(models.Model):
    """
    Table of grades computed offline for a given user and course.
    """
    user = models.ForeignKey(User, db_index=True)
    course_id = models.CharField(max_length=255, db_index=True)

    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    gradeset = models.TextField(null=True, blank=True)		# grades, stored as JSON

    class Meta:
        unique_together = (('user', 'course_id'), )

    def __unicode__(self):
        return "[OfflineComputedGrade] %s: %s (%s) = %s" % (self.user, self.course_id, self.created, self.gradeset)


class OfflineComputedGradeLog(models.Model):
    """
    Log of when offline grades are computed.
    Use this to be able to show instructor when the last computed grades were done.
    """
    class Meta:
        ordering = ["-created"]
        get_latest_by = "created"

    course_id = models.CharField(max_length=255, db_index=True)
    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    seconds = models.IntegerField(default=0)  	# seconds elapsed for computation
    nstudents = models.IntegerField(default=0)

    def __unicode__(self):
        return "[OCGLog] %s: %s" % (self.course_id, self.created)


class XModuleStudentStateDjangoBackend(object):

    def __init__(self, dbname="default"):
        self.dbname = dbname

    def __repr__(self):
        return u"XModuleStudentStateDjangoBackend({})".format(self.dbname)

    def _django_model_to_state_obj(self, model_record):
        return XModuleStudentState(
            model_record.course_id,
            model_record.student_id,
            model_record.module_state_key,
            module_type=model_record.module_type,
            state=model_record.state,
            grade=model_record.grade,
            max_grade=model_record.max_grade
        )

    def get(self, course_id, user_id, module_state_key):
        try:
            record = StudentModule.objects.using(self.dbname).get(
                course_id=course_id,
                student_id=user_id,
                module_state_key=module_state_key
            )
            return self._django_model_to_state_obj(record)
        except StudentModule.DoesNotExist:
            searched_for = (
                "(course_id={}, user_id={}, module_state_Key={}"
                .format(course_id, user_id, module_state_key)
            )
            raise KeyError(
                "Could not find XModuleStudentState for {} using {!r}"
                .format(searched_for, self)
            )

    def get_or_create(self, course_id, user_id, module_state_key, defaults):
        record, created = StudentModule.objects.using(self.dbname).get_or_create(
            course_id=course_id,
            student_id=user_id,
            module_state_key=module_state_key,
            defaults=defaults
        )
        return self._django_model_to_state_obj(record)

    def get_for_course_user(self, course_id, user_id, module_state_keys):
        records = StudentModule.objects.using(self.dbname).filter(
            course_id=course_id,
            student_id=user_id,
            module_state_key__in=module_state_keys
        )
        return [self._django_model_to_state_obj(record) for record in records]

    def save(self, state_obj):
        record, created = StudentModule.objects.using(self.dbname).get_or_create(
            course_id=state_obj.course_id,
            student_id=state_obj.user_id,
            module_state_key=state_obj.module_state_key
        )
        record.module_type = state_obj.module_type
        record.state = state_obj.state
        record.grade = state_obj.grade
        record.max_grade = state_obj.max_grade

        record.save()

    def delete(self, state_obj):
        record = StudentModule.objects.using(self.dbname).get(
            course_id=state_obj.course_id,
            student_id=state_obj.user_id,
            module_state_key=state_obj.module_state_key
        )
        record.delete()

class XModuleStudentStateMongoBackend(object):

    def __init__(self, host, db,
                 port=27017, collection="studentstate", user=None, password=None):
        conn = pymongo.connection.Connection(host=host, port=port, tz_aware=True)
        database = conn[db]
        self.collection = pymongo.collection.Collection(database, collection)

        # Authenticate if credentials provided
        if user is not None and password is not None:
            database.authenticate(user, password)

        self.collection.ensure_index(
            [("course_id", 1), ("user_id", 1), ("module_state_key", 1)],
            unique=True
        )

    def _mongo_model_to_state_obj(self, model_record):
        return XModuleStudentState(
            model_record['course_id'],
            model_record['user_id'],
            model_record['module_state_key'],
            module_type=model_record['module_type'],
            state=model_record['state'],
            grade=model_record['grade'],
            max_grade=model_record['max_grade']
        )

    def get(self, course_id, user_id, module_state_key):
        record = self.collection.find_one({
            "course_id" : course_id,
            "user_id" : user_id,
            "module_state_key" : module_state_key
        })
        if record is None:
            searched_for = (
                "(course_id={}, user_id={}, module_state_Key={}"
                .format(course_id, user_id, module_state_key)
            )
            raise KeyError(
                "Could not find XModuleStudentState for {} using {!r}"
                .format(searched_for, self)
            )
        return self._mongo_model_to_state_obj(record)

    def get_for_course_user(self, course_id, user_id, module_state_keys):
        records = self.collection.find({
            "course_id" : course_id,
            "user_id" : user_id,
            "module_state_key" : {
                "$in" : module_state_keys
            }
        })
        return [self._mongo_model_to_state_obj(record) for record in records]

    def get_or_create(self, course_id, user_id, module_state_key, defaults):
        """This probably isn't very idiomatic."""
        try:
            state_obj = self.get(course_id, user_id, module_state_key)
        except KeyError:
            state_obj = XModuleStudentState(
                course_id=course_id,
                user_id=user_id,
                module_state_key=module_state_key
            )
        for key, val in defaults.items():
            setattr(state_obj, key, val)
        state_obj.save()
        return state_obj

    def save(self, state_obj):
        self.collection.find_and_modify(
            query={
                "course_id" : state_obj.course_id,
                "user_id" : state_obj.user_id,
                "module_state_key" : state_obj.module_state_key,
            },
            update={
                "course_id" : state_obj.course_id,
                "user_id" : state_obj.user_id,
                "module_state_key" : state_obj.module_state_key,
                "module_type" : state_obj.module_type,
                "state" : state_obj.state,
                "grade" : state_obj.grade,
                "max_grade" : state_obj.max_grade
            },
            upsert=True
        )

    def delete(self, state_obj):
        self.collection.remove(
            {
                "course_id" : state_obj.course_id,
                "user_id" : state_obj.user_id,
                "module_state_key" : state_obj.module_state_key,
            },
        )


class XModuleStudentState(object):
    """
    Represents the state of a given XBlock usage for a given user
    (Scope.user_state in XBlock-speak). Meant to act as an abstraction layer
    over StudentModule, which is a Django-ORM specific backend. Unlike the
    XModule*Field classes above, this object stores multiple fields in one
    entry.
    """
    @classmethod
    def backend_for_course(cls, course_id):
        # If we haven't defined any alternate storage engines, just use the
        # default Django Backend.
        if not settings.STUDENT_STATE_STORAGE_ENGINES:
            return XModuleStudentStateDjangoBackend()

        # Now let's try to look up where this course should store its data
        storage_name = settings.STUDENT_STATE_STORAGE_FOR_COURSE.get(course_id, "default")
        engine = settings.STUDENT_STATE_STORAGE_ENGINES[storage_name]

        # Ok, this should actually be a part of the backends
        if engine["type"] == "sql":
            return XModuleStudentStateDjangoBackend(engine["db"])
        elif engine["type"] == "mongo":
            return XModuleStudentStateMongoBackend(
                host=engine["host"],
                db=engine["db"],
                collection=engine["collection"]
            )

        return XModuleStudentStateDjangoBackend()

    @classmethod
    def get_for_course_user(cls, course_id, user_id, module_state_keys):
        """
        `module_state_keys` is an iterable of module_state_keys that we want to
        retrieve.
        """
        backend = cls.backend_for_course(course_id)
        return backend.get_for_course_user(
            course_id, user_id, module_state_keys
        )

    @classmethod
    def get(cls, course_id, user_id, module_state_key):
        backend = XModuleStudentState.backend_for_course(course_id)
        return backend.get(course_id, user_id, module_state_key)

    @classmethod
    def get_or_create(cls, course_id, user_id, module_state_key, defaults=None):
        backend = XModuleStudentState.backend_for_course(course_id)
        return backend.get_or_create(course_id, user_id, module_state_key, defaults)

    def delete(self):
        XModuleStudentState.backend_for_course(self.course_id).delete(self)

    def save(self):
        XModuleStudentState.backend_for_course(self.course_id).save(self)

    def __init__(self, course_id, user_id, module_state_key,
                 module_type='problem', state=None, grade=None, max_grade=None):
        self.course_id = course_id
        self.user_id = user_id
        self.module_state_key = module_state_key
        self.module_type = module_type
        self.state = state
        self.grade = grade
        self.max_grade = max_grade



