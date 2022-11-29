from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
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


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "book",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)

        book = data["book"]

        if book.inventory <= 0:
            raise ValidationError("We don`t have this book")

        return data

    def create(self, validated_data):
        with transaction.atomic():

            book = validated_data.pop("book")

            book.inventory -= 1
            book.save()

            validated_data["book"] = book

            return Borrowing.objects.create(**validated_data)


class BorrowingListSerializer(BorrowingSerializer):

    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book_title", "user_email", )


class BorrowingDetailSerializer(BorrowingSerializer):

    user = UserSerializer(many=False)
    book = BookSerializer(many=False)
