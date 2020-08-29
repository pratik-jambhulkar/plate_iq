from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from invoice.models import User, Invoice, Company
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


class InvoiceSerializer(serializers.ModelSerializer):
    purchaser = CompanySerializer()
    vendor = CompanySerializer()
    created_by = UserResponseSerializer()
    digitized_by = UserResponseSerializer()

    class Meta:
        model = Invoice
        fields = '__all__'
