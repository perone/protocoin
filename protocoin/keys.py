import binascii
import hashlib

import ecdsa
from . import util

class BitcoinPublicKey(object):
    """This is a representation for Bitcoin public keys. In this
    class you'll find methods to import/export keys from multiple
    formats. Use a hex string representation to construct a new
    public key or use the clas methods to import from another format.

    :param hexkey: The key in hex string format
    """
    key_prefix = '\x04'

    def __init__(self, hexkey):
        stringkey = hexkey.decode("hex")[1:]
        self.public_key = ecdsa.VerifyingKey.from_string(stringkey,
            curve=ecdsa.SECP256k1)
    
    @classmethod
    def from_private_key(klass, private_key):
        """This class method will create a new Public Key
        based on a private key.

        :param private_key: The private key
        :returns: a new public key
        """
        public_key = private_key.get_verifying_key()
        hexkey = public_key.to_string().encode("hex")
        return klass(hexkey)

    def to_string(self):
        """This method will convert the public key to
        a string representation.

        :returns: String representation of the public key
        """
        return self.key_prefix + self.public_key.to_string()

    def to_hex(self):
        """This method will convert the public key to
        a hex string representation.

        :returns: Hex string representation of the public key
        """
        hexkey = self.public_key.to_string().encode("hex")
        return self.key_prefix.encode("hex") + hexkey.upper()

    def to_address(self):
        """This method will convert the public key to
        a bitcoin address.

        :returns: bitcoin address for the public key
        """
        pubkeystr = self.to_string()
        sha256digest = hashlib.sha256(pubkeystr).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256digest)
        ripemd160_digest = ripemd160.digest()
        
        # Prepend the version info
        ripemd160_digest = '\x00' + ripemd160_digest
        
        # Calc checksum
        checksum = hashlib.sha256(ripemd160_digest).digest()
        checksum = hashlib.sha256(checksum).digest()
        checksum = checksum[:4]
        
        # Append checksum
        address = ripemd160_digest + checksum
        address_bignum = int('0x' + address.encode('hex'), 16)
        base58 = util.base58_encode(address_bignum)
        return '1' + base58

    def __repr__(self):
        return "<BitcoinPublicKey address=[%s]>" % self.to_address()

class BitcoinPrivateKey(object):
    """This is a representation for Bitcoin private keys. In this
    class you'll find methods to import/export keys from multiple
    formats. Use a hex string
    representation to construct a new Public Key or
    use the clas methods to import from another format.
    If no parameter is specified on the construction of
    this class, a new Private Key will be created.

    :param hexkey: The key in hex string format
    :param entropy: A function that accepts a parameter
                    with the number of bytes and returns
                    the same amount of bytes of random
                    data, use a good source of entropy.
                    When this parameter is ommited, the
                    OS entropy source is used.
    """
    wif_prefix = '\x80'

    def __init__(self, hexkey=None, entropy=None):
        if hexkey:
            stringkey = hexkey.decode("hex")
            self.private_key = \
                ecdsa.SigningKey.from_string(stringkey, curve=ecdsa.SECP256k1)
        else:
            self.private_key = \
                ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1,
                    entropy=entropy)

    @classmethod
    def from_string(klass, stringkey):
        """This method will create a new Private Key using
        the specified string data.

        :param stringkey: The key in string format
        :returns: A new Private Key
        """     
        hexvalue = stringkey.encode("hex")
        return klass(hexvalue)

    @classmethod
    def from_wif(klass, wifkey):
        """This method will create a new Private Key from a
        WIF format string.

        :param wifkey: The private key in WIF format
        :returns: A new Private Key
        """
        value = util.base58_decode(wifkey)
        hexkey = "%x" % value
        checksum = hexkey[-4*2:].decode("hex")
        key = hexkey[:-4*2].decode("hex")

        shafirst = hashlib.sha256(key).digest()
        shasecond = hashlib.sha256(shafirst).digest()

        if shasecond[:4]!=checksum:
            raise RuntimeError("Invalid checksum for the address.")

        return klass(key[1:].encode("hex"))

    def to_hex(self):
        """This method will convert the Private Key to
        a hex string representation.

        :returns: Hex string representation of the Private Key
        """
        hexkey = self.private_key.to_string().encode("hex")
        return hexkey.upper()

    def to_string(self):
        """This method will convert the Private Key to
        a string representation.

        :returns: String representation of the Private Key
        """
        return self.private_key.to_string()

    def to_wif(self):
        """This method will export the Private Key to
        WIF (Wallet Import Format).

        :returns:: The Private Key in WIF format.
        """
        extendedkey = self.wif_prefix + self.to_string()
        shafirst = hashlib.sha256(extendedkey).digest()
        shasecond = hashlib.sha256(shafirst).digest()
        checksum = shasecond[:4]
        extendedkey = extendedkey + checksum
        key_bignum = int('0x' + extendedkey.encode('hex'), 16)
        base58 = util.base58_encode(key_bignum)
        return base58

    def generate_public_key(self):
        """This method will create a new Public Key based on this
        Private Key. 

        :returns: A new Public Key
        """
        hexkey = self.to_hex().upper()
        return BitcoinPublicKey.from_private_key(self.private_key)

    def __repr__(self):
        return "<BitcoinPrivateKey hexkey=[%s]>" % self.to_hex()



