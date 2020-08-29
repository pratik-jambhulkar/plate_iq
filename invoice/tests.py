import json

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from invoice.models import User, Invoice
from invoice.serializers import UserSerializer, InvoiceSerializer


class TestUploadInvoiceAPI(APITestCase):
    base_dir = settings.BASE_DIR
    fixtures = [base_dir + '/invoice/fixtures/users.json',
                base_dir + '/invoice/fixtures/companies.json',
                base_dir + '/invoice/fixtures/invoices.json',
                base_dir + '/invoice/fixtures/invoice_items.json',
                ]

    def setUp(self):
        self.user = User.objects.get(email='jon.doe@plate.com')
        user_serializer = UserSerializer(self.user).data
        self.authentication_token = user_serializer['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication_token)
        self.url = reverse('invoices-upload')

    # API /invoice/upload - Test to successfully upload invoice and get mock invoice details
    def test_upload_api(self):
        invoice = SimpleUploadedFile("invoice.pdf", b"file_content", content_type="application/pdf")
        data = {'invoice': invoice}
        response = self.client.post(path=self.url, data=data, format='multipart', HTTP_ACCEPT='application/json')
        invoice_object = Invoice.objects.first()
        self.assertEqual(response.content, JsonResponse(InvoiceSerializer(invoice_object).data).content)

    # API /invoice/upload - Test unsupported content type
    def test_upload_unsupported_content_type_api(self):
        invoice = SimpleUploadedFile("invoice.pdf", b"file_content", content_type="image/png")
        data = {'invoice': invoice}
        response = self.client.post(path=self.url, data=data, format='multipart', HTTP_ACCEPT='application/json')
        error = {'invoice': ['File content type not supported. application/pdf recommended.']}
        self.assertEqual(json.loads(response.content), json.loads(JsonResponse(ValidationError(error).detail).content))

    # API /invoice/upload - Test unsupported file size
    def test_upload_unsupported_file_size(self):
        invoice = SimpleUploadedFile("invoice.pdf", b"file_content" * 1000000, content_type="application/pdf")
        data = {'invoice': invoice}
        response = self.client.post(path=self.url, data=data, format='multipart', HTTP_ACCEPT='application/json')
        error = {'invoice': ['Invoice size too large(must be less than 1 MB).']}
        self.assertEqual(json.loads(response.content), json.loads(JsonResponse(ValidationError(error).detail).content))
