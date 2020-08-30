from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from invoice.models import User, Invoice, Company
from invoice.permissions import InvoicePermission
from invoice.serializers import UserSerializer, InvoiceSerializer, CompanySerializer, UploadInvoiceSerializer, \
    InvoiceDigitizedSerializer, InvoiceCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed or edited.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, ]

    @action(methods=['post'], detail=False, url_name='upload', url_path='upload')
    def upload(self, request):
        """
        Upload invoice API takes pdf file as an input and returns non digitized invoice
        :param request:
        :return: Invoice Object
        """
        upload_serializer = UploadInvoiceSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        return JsonResponse(self.serializer_class(self.queryset.first()).data)

    @action(methods=['get'], detail=True, url_name='digitized_status', url_path='digitized-status')
    def digitized_status(self, request, *_, **__):
        """
        Invoice digitization status API
        :param request:
        :return: Digitization status and other details
        """
        invoice = self.get_object()
        return JsonResponse(InvoiceDigitizedSerializer(invoice).data)

    def retrieve(self, request, *_, **__):
        """
        Retrieve the details for the invoice if the invoice is digitized or if the user is a superuser
        :param request:
        :return: Invoice object
        """
        invoice = self.get_object()
        if request.user.is_superuser or invoice.digitized:
            return JsonResponse(self.serializer_class(invoice).data)
        else:
            return JsonResponse({'invoice': "The invoice is not digitized yet!"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_name='digitize', url_path='digitize')
    def digitize(self, request, *_, **__):
        """
        Digitize invoice API
        :param request:
        :return: Invoice details if invoice is successfully digitized
        """
        invoice = self.get_object()
        if not invoice.digitized:
            invoice.digitized = True
            invoice.digitized_by = request.user
            invoice.save()
            invoice.refresh_from_db()
            return JsonResponse(InvoiceDigitizedSerializer(invoice).data)
        return JsonResponse({'invoice': "The invoice is already digitized!"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        API to create an invoice with superuser
        :param request: data to create the invoice
        :param args:
        :param kwargs:
        :return:
        """
        invoice_serializer = InvoiceCreateSerializer(data=request.data)
        invoice_serializer.is_valid(raise_exception=True)
        invoice = invoice_serializer.save(created_by=request.user)
        return JsonResponse(self.serializer_class(invoice).data)

    def update(self, request, *args, **kwargs):
        """
        Update invoice API
        :param request: data to update the invoice
        :param args:
        :param kwargs:
        :return:
        """
        invoice = self.get_object()
        invoice_serializer = InvoiceCreateSerializer(invoice, data=request.data)
        invoice_serializer.is_valid(raise_exception=True)
        invoice = invoice_serializer.save()
        return JsonResponse(self.serializer_class(invoice).data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update invoice
        :param request: partial data
        :param args:
        :param kwargs:
        :return:
        """
        invoice = self.get_object()
        invoice_serializer = InvoiceCreateSerializer(invoice, data=request.data, partial=True)
        invoice_serializer.is_valid(raise_exception=True)
        invoice = invoice_serializer.save()
        return JsonResponse(self.serializer_class(invoice).data)

    def get_permissions(self):
        permissions = super().get_permissions()
        permissions.append(InvoicePermission())
        return permissions


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
