from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from invoice.models import User, Invoice, Company
from invoice.serializers import UserSerializer, InvoiceSerializer, CompanySerializer, UploadInvoiceSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        return UnAuthorisedRequest


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed or edited.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, ]

    @action(methods=['post'], detail=False, url_name='upload', url_path='upload')
    def upload(self, request, *args, **kwargs):
        upload_serializer = UploadInvoiceSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        return JsonResponse(self.serializer_class(self.queryset.first()).data)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, ]
