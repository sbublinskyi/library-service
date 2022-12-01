import datetime

from celery import shared_task

from library_service import telegram_bot
from borrowings.models import Borrowing


@shared_task
def outdated_borrowings():
    borrowings = Borrowing.objects.filter(
        expected_return_date__lt=datetime.datetime.today(), actual_return_date=None
    )

    for borrowing in borrowings:
        telegram_bot.send_message(
            "New Borrowing:\n"
            f"User {borrowing.user} didn't return the book\n"
            f"Book: {borrowing.book}\n"
            f"Should be returned in {borrowing.expected_return_date}"
        )

    return f"{borrowings.count()} users didn't return the book"
