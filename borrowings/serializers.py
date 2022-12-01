import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from library_service import telegram_bot
from borrowings.models import Borrowing
from user.serializers import UserSerializer


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

            return Borrowing.objects.create(**validated_data)


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "user_email",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    book = BookSerializer(many=False)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user",
            "book",
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
