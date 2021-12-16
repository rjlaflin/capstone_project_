from django.shortcuts import reverse
from django.test import TestCase, Client
from django.http import HttpRequest, HttpResponse
from django.db.models import ObjectDoesNotExist
from django.contrib.sessions.backends.base import SessionBase

from typing import List

from capstone_project.models import User, Goals
from capstone_project.viewsupport.message import Message, MessageQueue


class TestDeleteGoals(TestCase):
    def setUp(self):
        self.client = Client()

        self.supervisor_username = 'aaronrodgers'
        self.supervisor = User.objects.create(
            unique_id=self.supervisor_username,
            pwd='a-very-good-password',
            # pwd_tmp=False,
            user_type=User.UserType.Supervisor
        )

        self.staff_username = 'cmwojta'
        self.staff = User.objects.create(
            unique_id=self.staff_username,
            pwd='a-very-good-password',
            # password_tmp=False,
            user_type=User.UserType.Staff
        )

        # Add goal
        self.goal = 'Fold Bed'
        self.good_status = 4
        self.good_curr = 1

        self.deleted_goal = Goals.objects.create(
            goal=self.goal,
            statusofgoal=self.good_status,
            goalcurrency=self.good_curr
        )

        self.deleted_goal_two = Goals.objects.create(
            goal="brush teeth",
            statusofgoal=2,
            goalcurrency=0
        )

        self.valid_delete_url = reverse('goals-delete', args=(self.deleted_goal.id,))
        self.valid_delete_self = reverse('goals-delete', args=(self.deleted_goal_two.id,))
        self.invalid_delete_url = reverse('goals-delete', args=(340000,))
        # Only two goals were created so the max valid id is 2

        self.session = self.client.session
        self.session['user_id'] = self.supervisor.id
        self.session.save()

    def get_first_message(self, resp) -> Message:
        session = resp.client.session
        self.assertTrue('messages' in session, msg='Session does not contain any message')
        try:
            messages = MessageQueue.get(session)
            return messages[0]
        except KeyError:
            self.assertTrue(False, 'Session does not contain any messages')

    def test_supervisor_can_delete_existing_goal(self):
        resp = self.client.post(self.valid_delete_url, {})

        message: Message = self.get_first_message(resp)

        self.assertIsNotNone(resp, 'Post did not return value')
        self.assertRedirects(resp, reverse('goals'))

        self.assertTrue(message.type() is Message.Type.REGULAR, 'Did not send correct message type')
        self.assertEqual(message.message(), f'Successfully deleted goal {self.deleted_goal}',
                         'Did not return correct message')

    def test_delete_no_goal_redirects_with_error(self):
        resp = self.client.post(self.invalid_delete_url, {}, follow=False)

        message: Message = self.get_first_message(resp)

        self.assertIsNotNone(resp, 'Post did not return value')
        self.assertRedirects(resp, reverse('goals'))

        self.assertTrue(message.type() is Message.Type.ERROR, 'Did not send correct message type')
        self.assertEqual(message.message(), f'No goal with id {340000} exists', 'Did not return correct message')

    def test_staff_cannot_delete_any_goal(self):
        self.session['user_id'] = self.staff.id
        self.session.save()

        resp_post = self.client.post(reverse('goals-delete', args=(self.supervisor.id,)), {}, follow=False)
        resp_get = self.client.get(reverse('goals-delete', args=(self.supervisor.id,)), {}, follow=False)

        message_post = self.get_first_message(resp_post)
        message_get = self.get_first_message(resp_get)

        self.assertIsNotNone(resp_post, 'Post did not return value')
        self.assertIsNotNone(resp_get, 'Get did not return value')

        self.assertRedirects(resp_post, reverse('goals'))
        self.assertRedirects(resp_get, reverse('goals'))

        self.assertTrue(message_post.type() is Message.Type.ERROR, 'Did not send correct message type')
        self.assertEqual(message_post.message(), f'You do not have permission to delete goals',
                         'Did not return correct message')

        self.assertTrue(message_get.type() is Message.Type.ERROR, 'Did not send correct message type')
        self.assertEqual(message_get.message(), f'You do not have permission to delete goals',
                         'Did not return correct message')

    def test_no_session(self):
        del self.session['goalid']
        self.session.save()
        resp_post = self.client.post(self.valid_delete_url, {})
        resp_get = self.client.get(self.valid_delete_url, {})

        self.assertIsNotNone(resp_post, 'Post did not return value')
        self.assertIsNotNone(resp_get, 'Get did not return value')

        self.assertRedirects(resp_post, reverse('home'))
        self.assertRedirects(resp_get, reverse('home'))

    def test_delete_removes_goal(self):
        self.client.post(self.valid_delete_url, {}, follow=True)

        with self.assertRaises(ObjectDoesNotExist, msg='Did not remove from database'):
            Goals.objects.get(id=self.deleted_goal.id)
