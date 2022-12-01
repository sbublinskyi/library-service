import stripe
from django.http import HttpResponse
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

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
                borrowing__user_id=self.request.user.id
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
    def return_book(self, request, session_id=None):
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        payment.status = "PAID"
        payment.type = "FINE"
        payment.save()
        session = stripe.checkout.Session.retrieve(session_id)

        return HttpResponse('<html><body><h1>Thanks for your order, customer.name!</h1></body></html>')
