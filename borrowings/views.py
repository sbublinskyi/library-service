from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

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
                ]
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
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super(BorrowingViewSet, self).list(request, *args, **kwargs)
