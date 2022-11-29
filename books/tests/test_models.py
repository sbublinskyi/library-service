from django.test import TestCase

from books.models import Book


class ModelsTests(TestCase):
    def test_book_str(self):
        book = Book.objects.create(
            title="test_name",
            author="test_author",
            cover="Soft",
            inventory=50,
            daily_fee=13.44,
        )
        self.assertEqual(str(book), book.title)
