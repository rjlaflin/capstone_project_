from capstone_project.models import Goals, User
from typing import Union, Iterable, Optional
from django.core.exceptions import ObjectDoesNotExist
import more_itertools


class Goal:

    @staticmethod
    def create_goal(
            userforgoal: Union[User.UserType, int],
            statusofgoal: Union[Goals.GoalStatus, int],
            goalcurrency: Union[Goals.GoalCurrency, int],
            goal: str = '',
            notesforgoal: str = '',
    ) -> int:
        """
        Create Goal with mandatory goal type, user for goal, status, notes and goal currency and returns goal by id
        """
        if type(goalcurrency) is int:
            goalcurrency = Goals.curr_from_int(statusofgoal)

        if type(statusofgoal) is int:
            statusofgoal = Goals.status_from_int(statusofgoal)

        if type(userforgoal) is int:
            userforgoal = User.from_int(userforgoal)

        if goal is None or goal == '':
            raise TypeError('username cannot be blank')

        new_goal = Goals.objects.create(
            goal=goal,
            userforgoal=userforgoal,
            statusofgoal=statusofgoal,
            goalcurrency=goalcurrency,
            notesforgoal=notesforgoal,
        )
        return new_goal.id

    @staticmethod
    def get_goal_by_goal_id(goal_id) -> Optional[Goals]:
        """
        Get user by user id and returns User if it exists, otherwise returns None
        """
        try:
            return Goals.objects.get(id=goal_id)
        except Goals.DoesNotExist:
            return None

    @staticmethod
    def get_goal_by_goal_name(goal: str) -> Optional[Goals]:
        """
        Get user by login id and returns User if it exists, otherwise returns None
        """
        try:
            return Goals.objects.get(goal=goal)
        except Goals.DoesNotExist:
            return None

    @staticmethod
    def get_all_goals() -> Optional[Iterable[Goals]]:
        """
        Get all users if any exist otherwise return None
        """
        goal_set = Goals.objects.all()
        return goal_set if more_itertools.ilen(goal_set) > 0 else None
        # try:
        #     return Goals.objects.all()
        # except Goals.DoesNotExist:
        #     return None

    @staticmethod
    def delete_goal(id: int, keep_parents=False) -> bool:
        """
        Deletes User if it exists using the id and returns a boolean for confirmation
        """
        try:
            goal = Goals.objects.get(id=id)
            goal.delete()
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def check_status_type(status: Goals.GoalStatus):
        if status == Goals.GoalStatus.Great.value[0]:
            return Goals.GoalStatus.Great
        elif status == Goals.GoalStatus.Adequate.value[0]:
            return Goals.GoalStatus.Adequate
        elif status == Goals.GoalStatus.ExceedsAdequacy.value[0]:
            return Goals.GoalStatus.ExceedsAdequacy
        elif status == Goals.GoalStatus.NotAdequate.value[0]:
            return Goals.GoalStatus.NotAdequate
        else:
            return Goals.GoalStatus.NotComplete

    @staticmethod
    def check_curr_type(curr: Goals.GoalCurrency):
        if curr == Goals.GoalCurrency.Future_Goal.value[0]:
            return Goals.GoalCurrency.Future_Goal
        elif curr == Goals.GoalCurrency.Current_Goal.value[0]:
            return Goals.GoalCurrency.Current_Goal
        else:
            return Goals.GoalCurrency.Completed_Goal

    @staticmethod
    def update_goal(goals: Goals, status: Goals.GoalStatus, currency: Goals.GoalCurrency,
                    notes: Optional[str] = None, goal: Optional[str] = None):
        """
        Updates user for last name, first name, and phone.
        If field is None then does not update, if empty string then removes current.
        """
        if goal is not None:
            goals.goal = goal

        if status is not None:
            goals.statusofgoal = status

        if currency is not None:
            goals.goalcurrency = currency

        if notes is not None:
            goals.notes = notes

        goals.save()
