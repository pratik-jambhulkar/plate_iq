import re
from secrets import choice


def generate_invoice_number(length=5):
    """
    Generates a random string of length pass through the parameter from the set of all alpha-numeric characters
    :param length: length of numbers to be appended to invoice
    :return: Invoice number
    """
    key = 'INV' + 'x' * length
    return re.sub('x', lambda x: choice('0123456789'), key)
