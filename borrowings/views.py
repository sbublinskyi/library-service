from datetime import datetime, timedelta

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
    create_stripe_session,
)
from payments.models import Payment


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")

        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        current_user = self.request.user

        if not current_user.is_staff:
            queryset = queryset.filter(user=current_user)
        elif user_id:
            queryset = queryset.filter(user_id=int(user_id))

        if is_active == "True":
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "return_book":
            return BorrowingReturnSerializer

    def perform_create(self, serializer):
        payments = Payment.objects.filter(borrowing__user_id=self.request.user)
        for payment in payments:
            if payment.status == "PENDING":
                raise ValidationError(
                    "Please at first paid your previous borrowings"
                )
        serializer.save(user=self.request.user)

    @action(methods=["PUT"], url_path="return_book", detail=True)
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=self.request.data)
        book = borrowing.book
        if serializer.is_valid():
            if borrowing.actual_return_date is None:
                book.inventory += 1
                book.save()
                serializer.save()
                if (
                    borrowing.actual_return_date
                    > borrowing.expected_return_date
                ):
                    Payment.objects.get(borrowing=borrowing).delete()
                    fine_multiplier = 2
                    days_of_overdue = (
                        borrowing.actual_return_date
                        - borrowing.expected_return_date
                    ).days
                    money_to_pay = (
                        book.daily_fee * days_of_overdue * fine_multiplier
                    )
                    session_url, session_id = create_stripe_session(
                        book, money_to_pay
                    )
                    Payment.objects.create(
                        status="PENDING",
                        borrowing=borrowing,
                        type="PAYMENT",
                        session_url=session_url,
                        session_id=session_id,
                        money_to_pay=money_to_pay,
                    )
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.STR,
                description="Filter what is in borrowing",
                examples=[
                    OpenApiExample(
                        "Example",
                        summary="?is_active=True",
                        value="True",
                    )
                ],
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by users, only for admins",
                examples=[
                    OpenApiExample(
                        "Example",
                        summary="?user_id=1",
                        description="Filter only by single id",
                        value=3,
                    )
                ],
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super(BorrowingViewSet, self).list(request, *args, **kwargs)
