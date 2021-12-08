from capstone_project.models import User, Goals
from django.test import TestCase


class TestModels(TestCase):

    def setUp(self) -> None:
        self.maybe_type1 = '0'
        self.maybe_type2 = ''
        self.maybe_type3 = '5'

    def test_from_str(self):
        response = User.from_int(int(self.maybe_type1))
        self.assertEqual(User.UserType.Supervisor, response, msg='Expected Supervisor type returned.')

    def test_from_str_non_type(self):
        with self.assertRaises(TypeError):
            User.from_int(int(self.maybe_type3))

    def test_from_str_with_empty_maybe_type(self):
        with self.assertRaises(TypeError):
            User.from_int(int(self.maybe_type2))

    def test_from_status(self):
        response = Goals.status_from_int(int(self.maybe_type1))
        self.assertEqual(User.UserType.Supervisor, response, msg='Expected NotCompletedGoal type returned.')

    def test_from_status_non_type(self):
        with self.assertRaises(TypeError):
            Goals.status_from_int(int(self.maybe_type3))

    def test_from_status_with_empty_maybe_type(self):
        with self.assertRaises(TypeError):
            Goals.status_from_int(int(self.maybe_type2))

    def test_from_curr(self):
        response = Goals.curr_from_int(int(self.maybe_type1))
        self.assertEqual(User.UserType.Supervisor, response, msg='Expected Future Goal type returned.')

    def test_from_curr_non_type(self):
        with self.assertRaises(TypeError):
            Goals.curr_from_int(int(self.maybe_type3))

    def test_from_curr_with_empty_maybe_type(self):
        with self.assertRaises(TypeError):
            Goals.curr_from_int(int(self.maybe_type2))
