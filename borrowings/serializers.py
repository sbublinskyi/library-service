import datetime
import os

import stripe
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from library_service import telegram_bot
from borrowings.models import Borrowing
from payments.models import Payment
from user.serializers import UserSerializer


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
        success_url=("http://localhost:8000/api/"
                     "payments/success?session_id={CHECKOUT_SESSION_ID}"),
        cancel_url="http://localhost:8000/api/payments/cancel",
    )
    return session.url, session.id


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)

        book = data["book"]

        if book.inventory < 1:
            raise ValidationError("We don`t have this book now")

        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.pop("book")

            book.inventory -= 1
            book.save()

            validated_data["book"] = book
            telegram_bot.send_message(
                "New Borrowing:\n"
                f"User: {validated_data['user']}\n"
                f"Book: {validated_data['book']}\n"
            )
            borrowing = Borrowing.objects.create(**validated_data)
            money_to_pay = book.daily_fee * Borrowing.MAX_TERM
            session_url, session_id = create_stripe_session(book, money_to_pay)
            Payment.objects.create(
                status="PENDING",
                borrowing=borrowing,
                type="PAYMENT",
                session_url=session_url,
                session_id=session_id,
                money_to_pay=money_to_pay,
            )
            return borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    payment_url = serializers.URLField(source="payment.session_url")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "user_email",
            "payment_url",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    book = BookSerializer(many=False)
    payment_url = serializers.URLField(source="payment.session_url")
    payment_id = serializers.CharField(source="payment.session_id")
    payment_status = serializers.CharField(source="payment.status")
    money_to_pay = serializers.DecimalField(
        source="payment.money_to_pay", max_digits=5, decimal_places=2
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
            "book",
            "payment_status",
            "payment_url",
            "payment_id",
            "money_to_pay",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField()

    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)

    def validate(self, attrs):
        if attrs["actual_return_date"] < datetime.date.today():
            raise ValidationError("Wrong date!")

        return super(BorrowingReturnSerializer, self).validate(attrs)
