from django.test import TestCase
from capstone_project.viewsupport.errors import PageError
from enum import Enum


class TestErrorPlace(Enum):
    ZERO = 0
    ONE = 1


TestError = PageError[TestErrorPlace]


class TestConcretePageError(TestCase):

    def setUp(self) -> None:
        self.message = 'A Message'
        self.place = TestErrorPlace.ONE

        self.error = TestError(
            self.message,
            self.place
        )

    def test_returns_message(self):
        self.assertEqual(self.message, self.error.message(), 'Did not return correct message')

    def test_returns_place(self):
        self.assertEqual(self.place, self.error.place(), 'Did not return correct place')
