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


class StatusTable(models.Model):
    NotComplete = 0
    NotAdequate = 1
    Adequate = 2
    ExceedsAdequacy = 3
    Great = 4


class GoalCurrency(models.Model):
    Non_Current_Goal = 0
    Current_Goal = 1
    Future_Goal = 2