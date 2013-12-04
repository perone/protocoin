# The Base58 digits
base58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(address_bignum):
    """This function converts an address in bignum formatting
    to a string in base58, it doesn't prepend the '1' prefix
    for the Bitcoin address.

    :param address_bignum: The address in numeric format
    :returns: The string in base58
    """
    basedigits = []
    while address_bignum > 0:
        address_bignum, rem = divmod(address_bignum, 58)
        basedigits.insert(0, base58_digits[rem])
    return ''.join(basedigits)

def base58_decode(address):
    """This function converts an base58 string to a numeric
    format.

    :param address: The base58 string
    :returns: The numeric value decoded
    """
    address_bignum = 0
    for char in address:
        address_bignum *= 58
        digit = base58_digits.index(char)
        address_bignum += digit
    return address_bignum