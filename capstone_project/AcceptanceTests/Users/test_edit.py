from django.shortcuts import reverse
from django.test import TestCase, Client
from django.http import HttpRequest, HttpResponse
from django.db.models import ObjectDoesNotExist
from typing import Optional

from capstone_project.models import User
from capstone_project.AcceptanceTests.acceptance_tests_base import AcceptanceTestCase
from capstone_project.viewsupport.errors import UserEditError, UserEditPlace
from capstone_project.viewsupport.message import Message, MessageQueue


class TestEditUser(AcceptanceTestCase[UserEditError]):
    def setUp(self):
        self.client = Client()
        self.session = self.client.session
        self.old_password = 'a-very-good-password'
        self.new_password = 'another-lesser-password'
        self.new_insurance = 'this is very good insurance information'

        self.supervisor_username = 'cmwojta'
        self.supervisor = User.objects.create(
            unique_id=self.supervisor_username,
            pwd=self.old_password,
            # pwd_tmp=False,
            user_type=User.UserType.Supervisor
        )

        self.supervisor_name_url = reverse('name', args=(self.supervisor.id,))
        self.supervisor_pw_url = reverse('user_pwd', args=(self.supervisor.id,))
        self.supervisor_insur_url = reverse('user_insurance', args=(self.supervisor.id,))
        self.supervisor_type_url = reverse('user', args=(self.supervisor.id,))

        self.staff_username = 'arodgers12'
        self.staff = User.objects.create(
            unique_id=self.staff_username,
            pwd=self.old_password,
            # pwd_tmp=False,
            user_type=User.UserType.Staff
        )

        self.staff_name_url = reverse('edit_name', args=(self.staff.id,))
        self.staff_insur_url = reverse('edit_insurance', args=(self.staff.id,))

    def set_supervisor_session(self):
        self.session['id'] = self.supervisor.id
        self.session.save()

    def set_staff_session(self):
        self.session['id'] = self.staff.id
        self.session.save()

    def test_edit_self_contact(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_name_url, {
            'user': 'new username',
            'user_insurance': 'this is very good insurance information'
        }, follow=False)

        self.assertContainsMessage(resp, Message('Username Updated'))

        self.assertRedirects(
            resp,
            reverse('update_successful', args=(self.supervisor.id,))
        )

    def test_edit_self_contact(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_insur_url, {
            'user': self.supervisor_username,
            'user_insurance': 'this is good insurance information'
        }, follow=False)

        self.assertContainsMessage(resp, Message('Contact Information Updated'))

        self.assertRedirects(
            resp,
            reverse('update_successful', args=(self.supervisor.id,))
        )

    def test_edit_self_password(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_pw_url, {
            'user': self.supervisor_username,
            'user_pwd': self.new_password,
        }, follow=False)

        self.assertContainsMessage(resp, Message('Password Updated'))

        self.assertRedirects(
            resp,
            reverse('update_successful', args=(self.supervisor.id,)),
        )

    def test_edit_self_updates_database(self):
        # This test uses the staff to update self instead of supervisor, to cover more use cases
        self.set_staff_session()
        resp = self.client.post(self.staff_name_url, {
            'user': 'self.staff_username',
            'user_insurance': self.new_insurance,
        }, follow=False)

        new_staff = User.objects.get(unique_id=self.staff_username)

        self.assertIsNotNone(new_staff)
        self.assertEqual(new_staff.insurance_information, self.new_insurance,
                         'Did not change contact information in database')

    def test_supervisor_edit_other_updates_database(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_insur_url, {
            'user': self.staff_username,
            'user_insurance': self.new_insurance,
        }, follow=False)

        new_staff = User.objects.get(unique_id=self.staff_username)

        self.assertIsNotNone(new_staff)
        self.assertEqual(new_staff.insurance_information, self.new_insurance,
                         'Did not change contact information in database')

    def test_rejects_supervisor_edit_other_password(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_pw_url, {
            'user': self.staff_username,
            'user_pwd': self.new_password,
        }, follow=False)

        self.assertContainsMessage(resp, Message('You may not change another users password', Message.Type.ERROR))

        # self.assertDoesNotRedirect(resp, 'Tried to redirect after failing to update user')

    def test_supervisor_edit_other_type(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_type_url, {
            'user': self.staff_username,
            'user_type': '0'
        }, follow=False)

        self.assertContainsMessage(
            resp,
            Message(f'User {self.staff.username} is now a Supervisor')
        )

        self.assertRedirects(resp, reverse('add_goal', args=(self.staff.id,)))

    def test_rejects_empty_username(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_pw_url, {
            'user': ''

        }, follow=True)

        error = self.assertContextError(resp)

        self.assertTrue(error.place() is UserEditPlace.USERNAME,
                        msg='Didn\'t return username error when attempting to remove username.')
        self.assertEqual(error.message(), 'You can\'t remove a user\'s username.')

    def test_rejects_too_long_username(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_name_url, {
            'user': 'a-very-long-username-that-the-database-could-not-hold'

        }, follow=True)

        error = self.assertContextError(resp)
        self.assertTrue(error.place() is UserEditPlace.USERNAME,
                        msg='Should have received an error about an username that was too long.')
        self.assertEqual(error.message(), 'A username may not be longer than 20 characters.')

    def test_rejects_incorrect_password_change(self):
        self.session['user_id'] = self.supervisor.id
        self.session.save()

        resp = self.client.post(self.supervisor_pw_url, {
            'user': self.supervisor_username,
            'user_pwd': self.new_password,
        }, follow=True)

        error = self.assertContextError(resp)
        self.assertTrue(error.place() is UserEditPlace.PASSWORD,
                        msg='Should have received an error about incorrect password.')
        self.assertEqual(error.message(), 'Incorrect password')

    def test_rejects_empty_password_change(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_pw_url, {
            'user': self.supervisor_username,
            'user_pwd': ''
        }, follow=True)

        error = self.assertContextError(resp)
        self.assertTrue(error.place() is UserEditPlace.PASSWORD,
                        msg='Should have recieved an error about empty new password.')
        self.assertEqual(error.message(), 'New password can\'t be empty.')

    def test_rejects_too_short_password_change(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_pw_url, {
            'user': self.supervisor_username,
            'user_pwd': '1234',
        }, follow=True)

        error = self.assertContextError(resp)
        self.assertTrue(error.place() is UserEditPlace.PASSWORD,
                        msg='Should have received an error about new password being too short.')
        self.assertEqual(error.message(), 'New Password needs to be 8 or more characters.')

    def test_rejects_invalid_insurance(self):
        self.set_supervisor_session()
        resp = self.client.post(self.supervisor_insur_url, {
            'user': self.supervisor_username,
            'user_insurance': 'good insurance'
        }, follow=True)

        error = self.assertContextError(resp)

        self.assertTrue(error.place() is UserEditPlace.INSURANCE,
                        msg='Should have received an error about incorrect insurance edit.')
        self.assertEqual(error.message(), 'Insurance needs to be longer than 20 characters or empty.')

    def test_rejects_non_supervisor_edit_other(self):
        self.set_staff_session()
        resp_post = self.client.post(self.staff_insur_url, {
            'user': self.supervisor_username,
            'user_insurance': 'good insurance'
        }, follow=False)

        self.assertContainsMessage(resp_post, Message('You are not allowed to edit other users.', Message.Type.ERROR))

        self.assertRedirects(resp_post, reverse('home_instructor'))

        resp_get = self.client.get(self.supervisor_insur_url, {}, follow=False)

        self.assertContainsMessage(resp_get, Message('You are not allowed to edit other users.', Message.Type.ERROR))

        self.assertRedirects(resp_get, reverse('home_instructor'))

