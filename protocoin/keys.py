import ecdsa
import hashlib
from . import util

class BitcoinPublicKey(object):
    key_prefix = '\x04'

    def __init__(self, hexkey):
        stringkey = hexkey.decode("hex")
        self.public_key = ecdsa.VerifyingKey.from_string(stringkey,
            curve=ecdsa.SECP256k1)
    
    @classmethod
    def from_private_key(klass, private_key):
        public_key = private_key.get_verifying_key()
        hexkey = public_key.to_string().encode("hex")
        return klass(hexkey)

    def to_string(self):
        return self.key_prefix + self.public_key.to_string()

    def to_hex(self):
        hexkey = self.public_key.to_string().encode("hex")
        return self.key_prefix.encode("hex") + hexkey.upper()

    def to_address(self):
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

class BitcoinPrivateKey(object):
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
        hexvalue = stringkey.encode("hex")
        return klass(hexvalue)

    def to_hex(self):
        hexkey = self.private_key.to_string().encode("hex")
        return hexkey.upper()

    def generate_public_key(self):
        hexkey = self.to_hex().upper()
        return BitcoinPublicKey.from_private_key(self.private_key)


