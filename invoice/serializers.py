from django.db import transaction
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from invoice.models import User, Invoice, Company, InvoiceItem
from invoice.utils import generate_invoice_number
from invoice.validators import validate_invoice_file


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    @staticmethod
    def get_token(obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return 'JWT ' + token


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email')


class UploadInvoiceSerializer(serializers.Serializer):
    invoice = serializers.FileField(allow_empty_file=False, validators=[validate_invoice_file])

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        fields = ('invoice',)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    purchaser = CompanySerializer()
    vendor = CompanySerializer()
    created_by = UserResponseSerializer()
    digitized_by = UserResponseSerializer()
    invoice_items = InvoiceItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = '__all__'

    @staticmethod
    def get_total(obj):
        return obj.total


class InvoiceDigitizedSerializer(serializers.ModelSerializer):
    digitized_by = UserResponseSerializer()

    class Meta:
        model = Invoice
        fields = ('digitized', 'digitized_by', 'invoice_number')


class InvoiceItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ('name', 'description', 'quantity', 'price', 'amount')


class InvoiceCreateSerializer(serializers.ModelSerializer):
    purchaser = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), error_messages={
        'required': 'This field is required.',
        'does_not_exist': 'Invalid Purchaser provided.',
        'incorrect_type': 'Provide data in correct format.'
    })
    vendor = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), error_messages={
        'required': 'This field is required.',
        'does_not_exist': 'Invalid Vendor provided.',
        'incorrect_type': 'Provide data in correct format.'
    })
    invoice_items = serializers.ListField(child=InvoiceItemSerializer(), min_length=1)
    digitized = serializers.BooleanField(default=False)
    invoice_number = serializers.CharField(default=generate_invoice_number)

    @transaction.atomic
    def create(self, validated_data):
        invoice_items = validated_data.pop('invoice_items', [])
        invoice = self.Meta.model.objects.create(**validated_data)
        for invoice_item in invoice_items:
            invoice_item['invoice'] = invoice
            InvoiceItem.objects.create(**invoice_item)
        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get('invoice_items'):
            invoice_items = validated_data.pop('invoice_items')
            InvoiceItem.objects.create_items(instance, invoice_items)
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = Invoice
        fields = ('purchaser', 'vendor', 'invoice_items', 'invoice_number', 'terms', 'deu_date', 'digitized')
