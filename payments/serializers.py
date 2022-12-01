import os

import stripe
from django.db import transaction
from rest_framework import serializers

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingDetailSerializer
from payments.models import Payment

stripe.api_key = os.environ.get("API_KEY")


def create_stripe_session(book: Book, price: float) -> tuple:
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": book.title,
                    },
                    "unit_amount": int(price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/success",
        cancel_url="http://localhost:8000/cancel",
    )
    return session.url, session.id


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )
        read_only_fields = (
            "money_to_pay",
            "session_url",
            "session_id",
        )

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = validated_data["borrowing"]
            book = borrowing.book
            money_to_pay = book.daily_fee * Borrowing.MAX_TERM
            session_url, session_id = create_stripe_session(book, money_to_pay)
            return Payment.objects.create(
                status=validated_data["status"],
                borrowing=borrowing,
                type=validated_data["type"],
                session_url=session_url,
                session_id=session_id,
                money_to_pay=money_to_pay,
            )


class PaymentDetailSerializer(serializers.ModelSerializer):

    borrowing = BorrowingDetailSerializer()

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )
