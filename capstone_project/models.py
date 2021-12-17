from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):

    class UserType(models.IntegerChoices):
        Supervisor = '0', _('Supervisor')
        Staff = '1', _('Staff')
        Patient = '2', _('Patient')

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    unique_id = models.CharField(max_length=50)
    pwd = models.CharField(max_length=30)
    user_type = models.IntegerField(
        choices=UserType.choices,
        default=UserType.Patient
    )
    insurance_information = models.CharField(max_length=1000)

    @classmethod
    def from_int(cls, maybe_type: int, user_types: dict = None) -> UserType:
        """
        Try to translate a UserType int, as stored in the database and returned from templates, into a
        UserType object. Must be in the set ["0", "1", "2"].
        Raises TypeError if it is not in said set.
        """
        if user_types is None:
            user_types = dict([('0', User.UserType.Supervisor), ('1', User.UserType.Staff),
                               ('2', User.UserType.Patient)])
        for key in user_types:
            if maybe_type == key:
                return user_types[key]
        raise TypeError(f'user_type {maybe_type} is not in the set of {user_types}')

    @classmethod
    def try_from_int(cls, maybe_type: int) -> Optional[UserType]:
        try:
            return cls.from_int(maybe_type)
        except TypeError:
            return None


class StatusTable(models.Model):
    NotComplete = 0
    NotAdequate = 1
    Adequate = 2
    ExceedsAdequacy = 3
    Great = 4


class Goals(models.Model):

    class GoalCurrency(models.IntegerChoices):
        Completed_Goal = 0, _('Completed Goal')
        Current_Goal = 1, _('Current Goal')
        Future_Goal = 2, _('Future Goal')

    class GoalStatus(models.IntegerChoices):
        NotComplete = 0, _('NotCompletedGoal')
        NotAdequate = 1, _('NotAdequate')
        Adequate = 2, _('Adequate')
        ExceedsAdequacy = 3, _('ExceedsAdequacy')
        Great = 4, _('Great')

    id = models.IntegerField(primary_key=True)
    goal = models.CharField(max_length=400, default=None)
    userforgoal = models.ForeignKey(User, on_delete= models.CASCADE, default=None)
    statusofgoal = models.IntegerField(
        choices=GoalStatus.choices,
        default=GoalStatus.NotComplete
    )
    notesforgoal = models.CharField(max_length=400, default=None)
    goalcurrency = models.IntegerField(
        choices=GoalCurrency.choices,
        default=GoalCurrency.Future_Goal
    )

    @classmethod
    def curr_from_int(cls, maybe_type: int, goalcurr: dict = None) -> GoalCurrency:
        """
        Try to translate a Goal Currency int, as stored in the database and returned from templates, into a
        Goal Currency object. Must be in the set ["0", "1", "2"].
        Raises TypeError if it is not in said set.
        """
        if goalcurr is None:
            goalcurr = dict([('0', Goals.GoalCurrency.Future_Goal), ('1', Goals.GoalCurrency.Current_Goal),
                          ('2', Goals.GoalCurrency.Completed_Goal)])
        for key in goalcurr:
            if maybe_type == key:
                return goalcurr[key]
        raise TypeError(f'goalcurr {maybe_type} is not in the set of {goalcurr}')

    @classmethod
    def curr_try_from_int(cls, maybe_type: int) -> Optional[GoalCurrency]:
        try:
            return cls.curr_from_int(maybe_type)
        except TypeError:
            return None

    @classmethod
    def status_from_int(cls, maybe_type: int, goalstat: dict = None) -> GoalStatus:
        """
        Try to translate a Goal Status int, as stored in the database and returned from templates, into a
        Goal Status object. Must be in the set ["0", "1", "2", "3", "4"].
        Raises TypeError if it is not in said set.
        """
        if goalstat is None:
            goalstat = dict([('0', Goals.GoalStatus.NotComplete), ('1', Goals.GoalStatus.NotAdequate),
                             ('2', Goals.GoalStatus.Adequate), ('3', Goals.GoalStatus.ExceedsAdequacy),
                             ('4', Goals.GoalStatus.Great)])
        for key in goalstat:
            if maybe_type == key:
                return goalstat[key]
        raise TypeError(f'goalstat {maybe_type} is not in the set of {goalstat}')

    @classmethod
    def status_try_from_int(cls, maybe_type: int) -> Optional[GoalStatus]:
        try:
            return cls.status_from_int(maybe_type)
        except TypeError:
            return None


'''
Assign Staff patients, not yet working

class Assignment(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    max_patients = models.IntegerField(verbose_name='Maximum number of patients that this Staff member'
                                                    ' can be assigned', blank=False)
'''
