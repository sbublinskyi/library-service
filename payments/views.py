from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(
                borrowing__user_id=self.request.user.id
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action in (
            "list",
            "create",
        ):
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
