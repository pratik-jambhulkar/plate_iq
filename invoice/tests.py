import json

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from invoice.models import User, Invoice
from invoice.serializers import UserSerializer, InvoiceSerializer, InvoiceDigitizedSerializer


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

    # API /invoices/pk/digitized - Test to check invoice is digitized without authentication
    def test_upload_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="wrong auth")
        invoice = SimpleUploadedFile("invoice.pdf", b"file_content", content_type="application/pdf")
        data = {'invoice': invoice}
        response = self.client.post(path=self.url, data=data, format='multipart', HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.assertEqual(api_response, {
            "detail": "Authentication credentials were not provided."
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestDigitizedStatusAPI(APITestCase):
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
        self.invoice = Invoice.objects.get(pk='INV12345')
        self.url = reverse('invoices-digitized_status', args=(self.invoice.invoice_number,))

    # API /invoices/pk/digitized-status - Test to check invoice is digitized
    def test_not_digitized_invoice(self):
        response = self.client.get(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        expected_response = json.loads(JsonResponse(InvoiceDigitizedSerializer(self.invoice).data).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(api_response['digitized'], False)

    # API /invoices/pk/digitized-status - Test to check invoice is digitized
    def test_digitized_invoice(self):
        invoice = Invoice.objects.get(pk='INV56789')
        url = reverse('invoices-digitized_status', args=(invoice.invoice_number,))
        response = self.client.get(path=url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        expected_response = json.loads(JsonResponse(InvoiceDigitizedSerializer(invoice).data).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(api_response['digitized'], True)

    # API /invoices/pk/digitized-status - Test to check invoice is digitized with invalid invoice number
    def test_invalid_invoice(self):
        url = reverse('invoices-digitized_status', args=("invalid123",))
        response = self.client.get(path=url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.assertEqual(api_response, {
            "detail": "Not found."
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # API /invoices/pk/digitized-status - Test to check invoice is digitized without authentication
    def test_digitized_status_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="wrong auth")
        response = self.client.get(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.assertEqual(api_response, {
            "detail": "Authentication credentials were not provided."
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestInvoiceRetrieveAPI(APITestCase):
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
        self.invoice = Invoice.objects.get(pk='INV56789')
        self.url = reverse('invoices-detail', args=(self.invoice.invoice_number,))

    # API /invoices/pk - Test to retrieve digitized invoice
    def test_digitized_invoice(self):
        response = self.client.get(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        expected_response = json.loads(JsonResponse(InvoiceSerializer(self.invoice).data).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(api_response['digitized'], True)

    # API /invoices/pk - Test to retrieve non digitized invoice
    def test_not_digitized_invoice(self):
        invoice = Invoice.objects.get(pk='INV12345')
        url = reverse('invoices-detail', args=(invoice.invoice_number,))
        response = self.client.get(path=url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        expected_response = json.loads(
            JsonResponse({'invoice': "The invoice is not digitized yet!"}, status=status.HTTP_400_BAD_REQUEST).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # API /invoices/pk - Test to retrieve with super user
    def test_retrieve_superuser(self):
        invoice = Invoice.objects.get(pk='INV12345')
        url = reverse('invoices-detail', args=(invoice.invoice_number,))
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(path=url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        expected_response = json.loads(JsonResponse(InvoiceSerializer(invoice).data).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(api_response['digitized'], False)

    # API /invoices/pk - Test to retrieve without authentication
    def test_retrieve_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="wrong auth")
        response = self.client.get(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.assertEqual(api_response, {
            "detail": "Authentication credentials were not provided."
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestDigitizeAPI(APITestCase):
    base_dir = settings.BASE_DIR
    fixtures = [base_dir + '/invoice/fixtures/users.json',
                base_dir + '/invoice/fixtures/companies.json',
                base_dir + '/invoice/fixtures/invoices.json',
                base_dir + '/invoice/fixtures/invoice_items.json',
                ]

    def setUp(self):
        self.user = User.objects.get(email='admin@plate.com')
        user_serializer = UserSerializer(self.user).data
        self.authentication_token = user_serializer['token']
        self.client.credentials(HTTP_AUTHORIZATION=self.authentication_token)
        self.invoice = Invoice.objects.get(pk='INV12345')
        self.url = reverse('invoices-digitize', args=(self.invoice.invoice_number,))

    # API /invoices/pk/digitize - Test to digitizing an invoice
    def test_digitize_invoice(self):
        response = self.client.post(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.invoice.refresh_from_db()
        expected_response = json.loads(JsonResponse(InvoiceDigitizedSerializer(self.invoice).data).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(api_response['digitized'], True)
        self.assertEqual(api_response['digitized_by']['email'], self.user.email)

    # API /invoices/pk/digitize - Test to digitizing a digitized invoice
    def test_digitize_digitized_invoice(self):
        self.invoice.digitized = True
        self.invoice.save()
        response = self.client.post(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        expected_response = json.loads(
            JsonResponse({'invoice': "The invoice is already digitized!"},
                         status=status.HTTP_400_BAD_REQUEST).content)
        self.assertEqual(api_response, expected_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # API /invoices/pk/digitize - Test to digitizing a digitized invoice with unauthenticated user
    def test_digitize_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="wrong auth")
        response = self.client.post(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.assertEqual(api_response, {
            "detail": "Authentication credentials were not provided."
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # API /invoices/pk/digitize - Test to digitizing a digitized invoice with unauthorised user
    def test_digitize_not_authorised(self):
        self.user.is_superuser = False
        self.user.save()
        response = self.client.post(path=self.url, HTTP_ACCEPT='application/json')
        api_response = json.loads(response.content)
        self.assertEqual(api_response, {
            "detail": "You do not have permission to perform this action."
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
