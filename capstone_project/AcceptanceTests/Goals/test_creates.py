from django.test import Client
from django.shortcuts import reverse
from django.db.models import ObjectDoesNotExist

from capstone_project.AcceptanceTests.acceptance_tests_base import AcceptanceTestCase
from capstone_project.viewsupport.errors import GoalEditError, GoalEditPlace
from capstone_project.viewsupport.message import Message, MessageQueue

from capstone_project.models import User, Goals


class TestGoalCreates(AcceptanceTestCase[GoalEditError]):

    def setUp(self):
        self.client = Client()
        self.session = self.client.session

        # Add user
        self.staff_user = User.objects.create(
            unique_id='cmwojta',
            pwd='password',
            user_type=User.UserType.Staff,
            # pwd_tmp=False
        )

        # Add user
        self.supervisor_user = User.objects.create(
            unique_id='chriswojta',
            pwd='greatpassword',
            user_type=User.UserType.Supervisor,
            # pwd_tmp=False
        )

        # Patient user
        self.patient_user = User.objects.create(
            unique_id='arodgers',
            pwd='password12',
            user_type=User.UserType.Patient,
            # pwd_tmp=False
        )

        # Add goal
        self.good_goal = 'Brush Teeth'
        self.good_notes = "doing very well"
        self.good_status = 2
        self.good_curr = 0
        self.goal = Goals.objects.create(
            goal=self.good_goal,
            userforgoal=self.patient_user.unique_id,
            statusofgoal=self.good_status,
            notesforgoal=self.good_notes,
            goalcurrency=self.good_curr
        )

        # Set current user
        self.session['user_id'] = self.supervisor_user.id
        self.session.save()

        self.url = reverse('add_goal')

    def test_creates(self):
        resp = self.client.post(self.url, {
            'goalinput': self.good_goal,
            'goalnotes': self.good_notes,
            'patient': self.patient_user.unique_id,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })

        goal = list(Goals.objects.all())[0]

        self.assertRedirects(resp, reverse('goals', args=[goal.id]))

        self.assertEqual(self.good_goal, goal.goal)
        self.assertEqual(self.good_notes, goal.notesforgoal)
        self.assertEqual(self.patient_user.unique_id, goal.userforgoal)
        self.assertEqual(self.good_curr, goal.goalcurrency)
        self.assertEqual(self.good_status, goal.statusofgoal)

    def test_rejects_missing_goal(self):
        resp = self.client.post(self.url, {
            # 'goalinput': self.good_goal,
            'goalnotes': self.good_notes,
            'patient': self.patient_user.unique_id,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error adding goal to the database. Try filling out the form again.')

        error = self.assertContextError(resp)

        self.assertEqual(GoalEditPlace.GOAL, error.place())
        self.assertEqual('Error with Adding Goal', error.message())
        # self.assertEqual(resp.context["message"], 'Error with Adding Goal',  msg='Error with Adding Goal')

    def test_rejects_missing_patient(self):
        resp = self.client.post(self.url, {
            'goalinput': self.good_goal,
            'goalnotes': self.good_notes,
            # 'patient': self.patient_user.unique_id,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error adding goal to the database. Try filling out the form again.')

        error = self.assertContextError(resp)

        self.assertEqual(GoalEditPlace.USER, error.place())
        self.assertEqual('Error with selecting Patient', error.message())

    def test_rejects_non_supervisor(self):
        self.session['user_id'] = self.staff_user
        self.session.save()

        resp = self.client.post(self.url, {
            'goalinput': self.good_goal,
            'goalnotes': self.good_notes,
            'patient': self.patient_user.unique_id,
            'goalcurrency': self.good_curr,
            'goalcompletionstatus': self.good_status
        })
        self.assertIsNotNone(resp, 'Error adding goal to the database. Try filling out the form again.')

        self.assertContainsMessage(resp, Message(
            'You do not have permission to create goals',
            Message.Type.ERROR,
        ))

        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(unique_id='arodgers')

        self.assertRedirects(resp, reverse('goals'))

