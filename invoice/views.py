from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from invoice.models import User, Invoice, Company
from invoice.serializers import UserSerializer, InvoiceSerializer, CompanySerializer, UploadInvoiceSerializer, \
    InvoiceDigitizedSerializer


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
    def upload(self, request):
        """
        Upload invoice API takes pdf file as an input and returns non digitized invoice
        :param request:
        :return: Invoice Object
        """
        upload_serializer = UploadInvoiceSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        return JsonResponse(self.serializer_class(self.queryset.first()).data)

    @action(methods=['get'], detail=True, url_name='digitized', url_path='digitized')
    def digitized(self, request, *_, **__):
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


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, ]
