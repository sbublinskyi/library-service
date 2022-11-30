from django.db import transaction
from rest_framework import serializers

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingDetailSerializer
from payments.models import Payment


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
        read_only_fields = ("money_to_pay",)

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = validated_data["borrowing"]

            money_to_pay = borrowing.book.daily_fee * Borrowing.MAX_TERM
            return Payment.objects.create(
                status=validated_data["status"],
                borrowing=borrowing,
                type=validated_data["type"],
                session_url=validated_data["session_url"],
                session_id=validated_data["session_id"],
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
