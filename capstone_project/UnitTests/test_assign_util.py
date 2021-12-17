import uuid
from capstone_project.ClassDesign.AssignUtil import AssignUtility
from capstone_project.models import User, Goals, Assignment

from django.test import TestCase


class TestAssignUtility(TestCase):

    def setUp(self) -> None:
        self.user1 = User.objects.create(user_type=User.UserType.Patient, unique_id='cmwojta', pwd='Password123')
        self.user2 = User.objects.create(user_type=User.UserType.Patient, unique_id='cwojta', pwd='Password456')
        self.user3 = User.objects.create(user_type=User.UserType.Staff, unique_id='arodgers', pwd='Password789')
        self.user4 = User.objects.create(user_type=User.UserType.Staff, unique_id='staff1', pwd='Password')

        self.goal1 = Goals.objects.create(
            goal="brushed teeth",
            userforgoal=self.user1,
            statusofgoal=1,
            notesforgoal="doing good job",
            goalcurrency=1
        )
        self.goal2 = Goals.objects.create(
            goal="make bed",
            userforgoal=self.user2,
            statusofgoal=0,
            notesforgoal="doing good job",
            goalcurrency=2
        )
        self.goal2.userforgoal = self.user2
        self.assignment1 = Assignment.objects.create(staff=self.user4, patient=self.user1, max_patients=1)
        self.assignment2 = Assignment.objects.create(staff=self.user3, max_patients=2)

    def test_assign_patient_to_goal(self):
        self.assertTrue(AssignUtility.assign_patient_to_goal(self.user1, self.goal1))

    def test_goal_already_has_patient_assigned(self):
        self.assertFalse(AssignUtility.assign_patient_to_goal(self.user2, self.goal2))

    def test_remove_patient_from_goal(self):
        self.assertTrue(AssignUtility.remove_patient_from_goal(self.user4, self.goal2))

    def test_assign_staff_to_patient(self):
        response = AssignUtility.assign_staff_to_patient(self.user3, self.user2, 2)
        self.assertEqual(True, response, msg='Expected the staff to be assigned to patient.')

    def test_staff_already_assigned_to_patient(self):
        response = AssignUtility.assign_staff_to_patient(self.user4, self.user2, 1)
        self.assertEqual(False, response, msg="Expected the staff not to be assigned because already assigned.")

    def test_remove_staff_from_patient(self):
        self.assertTrue(AssignUtility.remove_staff_from_patient(self.user3, self.user2))
        self.assertTrue(self.assignment1 is None, msg='Expected user3 to be removed from patient')

    def test_check_staff_assign_number(self):
        self.assertFalse(AssignUtility.check_staff_assign_number(self.user3))

    def tests_check_staff_assign_number_good(self):
        self.assertTrue(AssignUtility.check_staff_assign_number(self.user4))

    def test_update_staff_assign_number(self):
        self.assertTrue(AssignUtility.update_staff_assign_number(self.user4, 4))
        self.assignment2.refresh_from_db()
        self.assertEqual(4, self.assignment2.max_patients, msg='Expected new max_patients value to be 4.')
