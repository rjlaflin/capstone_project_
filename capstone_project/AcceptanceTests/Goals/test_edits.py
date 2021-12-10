from django.test import Client
from django.shortcuts import reverse
from django.db.models import ObjectDoesNotExist

from capstone_project.AcceptanceTests.acceptance_tests_base import AcceptanceTestCase
from capstone_project.viewsupport.errors import GoalEditError, GoalEditPlace
from capstone_project.viewsupport.message import Message, MessageQueue

from capstone_project.models import User, Goals


class TestGoalEdits(AcceptanceTestCase[GoalEditError]):

    def setUp(self):
        self.client = Client()
        self.session = self.client.session

        # Add supervisor
        self.supervisor_username = 'cmwojta'
        self.supervisor_user = User.objects.create(
            unique_id=self.supervisor_username,
            pwd='greatpassword',
            user_type=User.UserType.Supervisor,
            # pwd_tmp=False
        )

        self.supervisor_edit_url = reverse('edit_goal.html', args=(self.supervisor_user.id,))

        # Add staff
        self.staff_user = User.objects.create(
            unique_id='arodgers',
            pwd='password',
            user_type=User.UserType.Staff,
            # pwd_tmp=False
        )
        self.staff_edit_url = reverse('edit_goal.html', args=(self.staff_user.id,))

        # Patient user
        self.patient_username = 'cmwojta'
        self.patient_user = User.objects.create(
            unique_id= self.patient_username,
            pwd='password12',
            user_type=User.UserType.Patient,
            # pwd_tmp=False
        )

        # Add goal
        self.goal = 'Fold Bed'
        self.good_note = "show how to fold bed"
        self.good_status = 4
        self.good_curr = 1
        self.edited_goal = Goals.objects.create(
            goal=self.goal,
            statusofgoal=self.good_status,
            notesforgoal=self.good_note,
            goalcurrency=self.good_curr
        )

    def set_supervisor_user_session(self):
        self.session['user_id'] = self.supervisor_user.id
        self.session.save()

    def set_staff_session(self):
        self.session['user_id'] = self.staff_user.id
        self.session.save()

    def test_edit_goal(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': "Clean up mess",
            'goalnotes': self.good_note,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        }, follow=False)

        new_goal = Goals.objects.get(id=self.edited_goal.id)

        self.assertContainsMessage(resp, Message('Successfully edited goal.'))
        self.assertEqual(new_goal.goal, self.edited_goal.goal, 'Did not change goal in database')

        self.assertRedirects(
            resp,
            reverse('goals.html', args=(self.supervisor_user.id,))
        )

    def test_edit_notes(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': self.goal,
            'goalnotes': "Work on bettering this part",
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        }, follow=False)

        new_goal = Goals.objects.get(id=self.edited_goal.id)

        self.assertContainsMessage(resp, Message('Successfully edited goal.'))
        self.assertEqual(new_goal.notesforgoal, self.edited_goal.notesforgoal, 'Did not change goal in database')

        self.assertRedirects(
            resp,
            reverse('goals.html', args=(self.supervisor_user.id,))
        )

    def test_edit_currency(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': self.goal,
            'goalnotes': self.good_note,
            'goalcurrency': 0,
            'goalcompletionstatus': self.good_status
        }, follow=False)

        new_goal = Goals.objects.get(id=self.edited_goal.id)

        self.assertContainsMessage(resp, Message('Successfully edited goal.'))
        self.assertEqual(new_goal.goalcurrency, self.edited_goal.goalcurrency, 'Did not change goal in database')

        self.assertRedirects(
            resp,
            reverse('goals.html', args=(self.supervisor_user.id,))
        )

    def test_edit_status(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': self.goal,
            'goalnotes': self.good_note,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': 2
        }, follow=False)

        new_goal = Goals.objects.get(id=self.edited_goal.id)

        self.assertContainsMessage(resp, Message('Successfully edited goal.'))
        self.assertEqual(new_goal.statusofgoal, self.edited_goal.statusofgoal, 'Did not change goal in database')

        self.assertRedirects(
            resp,
            reverse('goals.html', args=(self.supervisor_user.id,))
        )

    def test_edit_goal_staff_database(self):
        # This test uses the staff to update goal instead of supervisor, to cover more use cases
        self.set_staff_session()
        resp = self.client.post(self.staff_edit_url, {
            'goalinput': self.goal,
            'goalnotes': self.good_note,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        }, follow=False)

        new_goal = Goals.objects.get(id=self.edited_goal.id)

        self.assertIsNotNone(new_goal)
        self.assertEqual(new_goal.goal, self.edited_goal.goal,
                         'Did not change contact information in database')
        self.assertEqual(new_goal.notesforgoal, self.edited_goal.notesforgoal,
                         'Did not change contact information in database')
        self.assertEqual(new_goal.goalcurrency, self.edited_goal.goalcurrency,
                         'Did not change contact information in database')
        self.assertEqual(new_goal.statusofgoal, self.edited_goal.statusofgoal,
                         'Did not change contact information in database')
        self.assertEqual(new_goal.goal, self.edited_goal.goal,
                         'Did not change contact information in database')

    def test_rejects_staff_edit_patients_not_assigned(self):
        self.set_staff_session()
        resp = self.client.post(self.staff_edit_url, {
            'goalinput': self.staff_username,
            'goalnotes': "can't edit patients goals not assigned to them",
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        }, follow=False)

        self.assertContainsMessage(resp, Message('You may not change a patients goals not assigned to you',
                                                 Message.Type.ERROR))

    def test_rejects_missing_goal(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            # 'goalinput': self.good_goal,
            'goalnotes': self.good_note,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error editing goal. Try filling out the form again.')

        error = self.assertContextError(resp)

        self.assertEqual(GoalEditPlace.GOAL, error.place())
        self.assertEqual('Goal input was not valid', error.message())

    def test_rejects_missing_notes(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': self.goal,
            # 'goalnotes': self.good_note,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error editing goal. Try filling out the form again.')

        error = self.assertContextError(resp)

        self.assertEqual(GoalEditPlace.GOAL, error.place())
        self.assertEqual('Goal notes input was not valid', error.message())

    def test_rejects_missing_currency(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': self.goal,
            'goalnotes': self.good_note,
            # 'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error editing goal. Try filling out the form again.')

        error = self.assertContextError(resp)

        self.assertEqual(GoalEditPlace.GOAL, error.place())
        self.assertEqual('Goal Currency selection input was not valid', error.message())

    def test_rejects_missing_status(self):
        self.set_supervisor_user_session()
        resp = self.client.post(self.supervisor_edit_url, {
            'goalinput': self.goal,
            'goalnotes': self.good_note,
            'goalcurrency': self.good_curr,
            # 'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error editing goal. Try filling out the form again.')

        error = self.assertContextError(resp)

        self.assertEqual(GoalEditPlace.GOAL, error.place())
        self.assertEqual('Goal Status Selected was not valid', error.message())
