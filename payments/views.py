import stripe
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentSuccessSerializer
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(
                borrowing__user=self.request.user
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        if self.action == "success":
            return PaymentSuccessSerializer

    @action(methods=["GET"], url_path="success", detail=False)
    def success(self, request, session_id=None):
        session_id = request.query_params.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
        if session["status"] == "complete":
            payment = Payment.objects.get(session_id=session_id)
            data = {
                "status": "PAID",
                "type": "FINE"
            }
            print(self.action)
            serializer = self.get_serializer(payment, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], url_path="cancel", detail=False)
    def cancel(self, request):
        raise ValidationError(
            "Payment can be paid a bit later (but the session is available for only 24h)"
        )
