import phonenumbers


def valid_phone(phone_number, country_code='US'):
    """
    Validate a phone number based on length, valid area codes
    and exchanges. Leverages the `Phone Numbers <https://github.com/daviddrysdale/python-phonenumbers>`_
    python library which is a port of Google ``libphonenumber``.

    `Args:`
        phone_number: str
           A phone number
        country_code: str
           The default country code
    """

    phone = phonenumbers.parse(str(phone_number), country_code)
    return phonenumbers.is_valid_number(phone)