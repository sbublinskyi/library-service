from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.tests.test_book_api import sample_book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def sample_borrowing(**params):
    defaults = {
        "borrow_date": "2022-11-30",
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass123",
        )
        self.client.force_authenticate(self.user)

    def test_filter_borrowing_by_active(self):
        book1 = sample_book()
        borrowing1 = sample_borrowing(book=book1, user=self.user)
        borrowing2 = sample_borrowing(book=book1, user=self.user)

        borrowing2.actual_return_date = "2022-12-01"

        res = self.client.get(BORROWING_URL, {"is_active": "True"})

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_borrowing_by_user_do_nothing_if_not_staff(self):
        book1 = sample_book()
        user2 = get_user_model().objects.create_user(
            "test2@test2.com",
            "testpass234"
        )
        borrowing1 = sample_borrowing(book=book1, user=self.user)
        borrowing2 = sample_borrowing(book=book1, user=user2)

        res = self.client.get(BORROWING_URL, {"user_id": 2})

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


class AdminBorrowingApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_filter_borrowing_by_user_id(self):
        book1 = sample_book()
        user2 = get_user_model().objects.create_user(
            "test2@test2.com",
            "testpass234"
        )
        borrowing1 = sample_borrowing(book=book1, user=self.user)
        borrowing2 = sample_borrowing(book=book1, user=user2)

        res = self.client.get(BORROWING_URL, {"user_id": "1"})

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
