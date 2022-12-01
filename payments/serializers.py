from rest_framework import serializers

from borrowings.serializers import BorrowingDetailSerializer
from payments.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="borrowing.user.email")

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
            "user",
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


class PaymentSuccessSerializer(serializers.ModelSerializer):
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
            "id",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )
