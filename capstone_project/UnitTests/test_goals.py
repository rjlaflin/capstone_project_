from capstone_project.ClassDesign.Goals import Goal
from capstone_project.ClassDesign.LoginUtil import LoginUtil
from django.test import TestCase
import more_itertools
from capstone_project.models import User, Goals


class TestGoal(TestCase):

    def setUp(self):
        self.goal = 'brushing teeth'
        self.notes = 'brush for 3 minutes'
        self.currgoal = Goals.GoalCurrency.Future_Goal
        self.statGoal = Goals.GoalStatus.NotComplete
        self.id1 = Goals.objects.create(
            goal=self.goal,
            userforgoal=User.UserType.Patient,
            statusofgoal=self.statGoal,
            notesforgoal=self.notes,
            goalcurrency=self.currgoal
            )
        self.id2 = Goals.objects.create(goal='make bed', userforgoal=User.UserType.Patient,
                                        statusofgoal=Goals.GoalStatus.NotComplete,
                                        goalcurrency=Goals.GoalCurrency.Current_Goal)

    def test_create_goal(self):
        goal_id = Goal.create_goal(User.UserType.Patient, self.currgoal, self.statGoal, self.goal, self.notes)
        self.assertTrue(goal_id > 0, msg='Expecting id returned confirming saved to database.')

    def test_get_goal_by_goal_id(self):
        goal = Goal.get_goal_by_goal_id(self.id1.id)
        self.assertEqual(self.id1.id, goal.id, msg='Goal id should be equal goalId1')

    def test_get_goal_by_goal_name(self):
        goal = Goal.get_goal_by_goal_name(self.goal)
        self.assertEqual(self.goal, goal.goal, msg='Goal should be equal to goal1s goal name.')

    def test_get_all_goals(self):
        goal_set = Goal.get_all_goals()
        list_of_goals = list(goal_set)
        length = more_itertools.ilen(list_of_goals)
        self.assertEqual(2, length, msg='Expected list of goals to be 2.')
        self.assertTrue(self.id1 in list_of_goals, msg='Expect goal1 in all courses.')
        self.assertTrue(self.id1 in list_of_goals, msg='Expected goal2 in all courses.')

    def test_delete_goal(self):
        response = Goal.delete_goal(self.id1.id)
        self.assertEqual(True, response, msg='Because we expect that the object is not in database.')

    def test_update_goal(self):
        goal = Goal.get_goal_by_goal_id(self.id2.id)
        notes = 'Make blanket more neat'
        status = Goals.GoalStatus.Great
        currency = Goals.GoalCurrency.Completed_Goal
        Goal.update_goal(goal, status, currency, notes)
        goal = Goal.get_goal_by_goal_id(self.id2.id)
        self.assertEqual(notes, goal.notesforgoal, msg='')
        self.assertEqual(status, goal.statusofgoal, msg='')
        self.assertEqual(currency, goal.goalcurrency, msg='')

    def test_check_status(self):
        goal = Goal.get_goal_by_goal_id(self.id1.id)
        self.assertEqual('0', goal.statusofgoal, msg="Expected goal status not complete as type for goal1")

    def test_check_currency(self):
        goals = Goal.get_goal_by_goal_id(self.id1.id)
        self.assertEqual('2', goals.goalcurrency, msg="Expected goal currency future goal as type for goal1")

    def test_empty_status(self):
        with self.assertRaises(TypeError):
            new_goal = Goal.create_goal(User.UserType.Patient, int(''), self.currgoal, self.goal, self.notes)

    def test_empty_currency(self):
        with self.assertRaises(TypeError):
            new_goal = Goal.create_goal(User.UserType.Patient, self.statGoal, int(''), self.goal, self.notes)

    def test_empty_user(self):
        new_goal = Goal.create_goal(int(''), self.statGoal, self.currgoal, self.goal, self.notes)
        goals = Goal.get_goal_by_goal_id(new_goal)
        self.assertTrue(goals.userforgoal, msg='User can not be empty')

    def test_empty_goal(self):
        with self.assertRaises(TypeError):
            new_goal = Goal.create_goal(User.UserType.Patient, self.statGoal, self.currgoal, '', self.notes)
