from rest_framework import serializers


def validate_invoice_file(invoice):
    """
    Validates the invoice uploaded
    :param invoice: Invoice file
    :return: returns Validated invoice or raises an Exception
    """
    if invoice.content_type != "application/pdf":
        raise serializers.ValidationError(
            'File content type not supported. application/pdf recommended.')
    if invoice.size > 1 * 1024 * 1024:
        raise serializers.ValidationError('Invoice size too large(must be less than 1 MB).')

    return invoice
