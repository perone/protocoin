Getting Started
===============================================================================
In this section you'll find a tutorial to learn more about Protocoin.

Installation
-------------------------------------------------------------------------------
To install Protocoin, use `pip` (recommended method) or `easy_install`::

    pip install protocoin

Architecture
-------------------------------------------------------------------------------
Protocoin uses a simple architecture of classes representing the data
to be serialized and also classes representing the types of the fields
to be serialized.

Protocoin is organized in four main submodules:

    * :py:mod:`protocoin.fields`
    * :py:mod:`protocoin.serializers`
    * :py:mod:`protocoin.clients`
    * :py:mod:`protocoin.keys`

Each module structure is described in the next sections.

Protocoin Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The :py:mod:`protocoin.fields` module contains all field types suported by the
serializers. All field classes inherit from the base :py:class:`protocoin.fields.Field` class,
so if you want to create a new field type, you should inherit from this class too. There
are some composite field types to help in common uses like the :py:class:`protocoin.fields.VariableStringField`
for instance, representing a string with variable length.

There are a lot of different fields you can use to extend the protocol, examples are: 
:py:class:`protocoin.fields.Int32LEField` (a 32-bit integer little-endian),
:py:class:`protocoin.fields.UInt32LEField` (a 32-bit unsigned int little-endian),
:py:class:`protocoin.fields.Int64LEField` (a 64-bit integer little-endian),
:py:class:`protocoin.fields.UInt64LEField` (a 64-bit unsigned integer little-endiang), etc. For
more information about the fields avaiable please see the module documentation.

Example of code for the unsigned 32-bit integer field::

    class UInt32LEField(Field):
        datatype = "<I"

        def parse(self, value):
            self.value = value

        def deserialize(self, stream):
            data_size = struct.calcsize(self.datatype)
            data = stream.read(data_size)
            return struct.unpack(self.datatype, data)[0]

        def serialize(self):
            data = struct.pack(self.datatype, self.value)
            return data      

Protocoin Serializers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Serializers are classes that describe the field types (in the correct order) that
will be used to serializer or deserialize the message or a part of a message, for
instance, see this example of a :py:class:`protocoin.serializers.IPv4Address` object
class and then its serializer class implementation::

    class IPv4Address(object):
        def __init__(self):
            self.services = fields.SERVICES["NODE_NETWORK"]
            self.ip_address = "0.0.0.0"
            self.port = 8333

    class IPv4AddressSerializer(Serializer):
        model_class = IPv4Address
        services = fields.UInt64LEField()
        ip_address = fields.IPv4AddressField()
        port = fields.UInt16BEField()

To serialize a message, you simple do::

    address = IPv4Address()
    serializer = IPv4AddressSerializer()
    binary_data = serializer.serialize(address)

and to deserialize::

    address = serializer.deserialize(binary_data)

.. warning:: It is important to subclass the :py:class:`protocoin.serializers.Serializer`
             class in order for the serializer to work, Serializers uses Python
             metaclasses magic to deserialize the fields using the correct types
             and also the correct order.

Note that we have a special attribute on the serializer that is defining the
`model_class` for the serializer, this class is used to instantiate the
correct object class in the deserialization of the data.

There are some useful fields you can use to nest another serializer or
a list of serializers inside a serializer, see in this example of the
implementation of the Version (:py:class:`protocoin.serializers.Version`) command::

    class VersionSerializer(Serializer):
        model_class = Version
        version = fields.Int32LEField()
        services = fields.UInt64LEField()
        timestamp = fields.Int64LEField()
        addr_recv = fields.NestedField(IPv4AddressSerializer)
        addr_from = fields.NestedField(IPv4AddressSerializer)
        nonce = fields.UInt64LEField()
        user_agent = fields.VariableStringField()

Note that the fields `addr_recv` and `addr_from` are using the special
field called :py:class:`protocoin.fields.NestedField`.

.. note:: There are other special fields like the :py:class:`protocoin.fields.ListField`,
          that will create a vector of objects using the correct Bitcoin format to serialize
          vectors of data.

Network Clients
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Protocoin also have useful classes to implement a network client for the Bitcoin
P2P network.

A basic network client
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The most basic class available to implement a client is the 
:py:class:`protocoin.clients.BitcoinBasicClient`, which is a simple client
of the Bitcoin network that accepts a socket in the constructor and then
will handle and route the messages received to the correct methods of the class,
see this example of a basic client::

    import socket
    from protocoin.clients import BitcoinBasicClient

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("bitcoin.sipa.be", 8333))
    client = BitcoinBasicClient(sock)
    client.loop()

Note that this client is very basic, in the example above, the client
will connect into the node **bitcoin.sipa.be** (a seed node) in the port 8333
and then will wait for messages. The :py:class:`protocoin.clients.BitcoinBasicClient`
class doesn't implement the handshake of the protocol and also doesn't
answer the pings of the nodes, so you may be disconnected from the node and
it is your reponsability to implement the handshake and the Pong response message
to the Ping message. To implement answer according to the received messages
from the network node, you can implement methods with the name **handle_[name of the
command]**, to implement the handling method to show a message every time
that a Version message arrives, you can do like in the example below::

    class MyBitcoinClient(BitcoinBasicClient):
        def handle_version(self, message_header, message):
            print "A version was received !"

If you want to answer the version command message with a VerAck message, you
just need to create the message, the serializer and then call the 
:py:meth:`protocoin.clients.BitcoinBasicClient.send_message` method of the
Bitcoin class, like in the example below::

    class MyBitcoinClient(BitcoinBasicClient):
        def handle_version(self, message_header, message):
            verack = VerAck()
            verack_serial = VerAckSerializer()
            self.send_message(verack, verack_serial)

Since these problems are very common, there are another class which implements
a node that will stay up in the Bitcoin network. To use this class, just 
subclass the :py:class:`protocoin.clients.BitcoinClient` class, for more information
read the next section.

A more complete client implementation
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The :py:class:`protocoin.clients.BitcoinClient` class implements the minimum
required protocol rules to a client stay online on the Bitcoin network. This
class will answer to Ping message commands with Pong messages and also have
a handshake method that will send the Version command and answer the Version
with the VerAck command message too. See an example of the use::

    import socket
    from protocoin.clients import BitcoinClient

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("bitcoin.sipa.be", 8333))
    client = BitcoinClient(sock)
    client.handshake()
    client.loop()

In the example above, the handshake is done before entering the message
loop.

Bitcoin Keys -- Creating, exporting/importing and conversions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The :py:mod:`protocoin.keys` module contains classes to represent and
handle Bitcoin Private Keys as well Public Keys. The two main classes
in this module are :py:class:`protocoin.keys.BitcoinPublicKey` and
:py:class:`protocoin.keys.BitcoinPrivateKey`. These classes contain
methods to generate new key pairs (Private and Public), to convert
the keys into Bitcoin addresses or Bitcoin WIF (Wallet Import Format)
and to import keys from different formats.

Creating Private Keys and Public Keys
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
In order to create a new Private Key, you only need to instantiate the
:py:class:`protocoin.keys.BitcoinPrivateKey` class without any parameter::

    from protocoin import keys
    priv_key = keys.BitcoinPrivateKey()
    print priv_key

The example above, will create a new Private Key called `priv_key` and will
output the string representation of the Private Key in hex::

    <BitcoinPrivateKey hexkey=[E005459416BE7FDC13FA24BA2F2C0DE289F47495D6E94CF2DFBC9FB941CBB565]>

You can now use this generated Private Key to create your Public Key like in
the example below::

    from protocoin import keys
    priv_key = keys.BitcoinPrivateKey()
    pub_key = priv_key.generate_public_key()
    print pub_key

This example will output::

    <BitcoinPublicKey address=[19eQMjBSeeo8fhCRPEVCfnauhsCFVGgV6H]>

Which is the Bitcoin address for the Public Key. You can also convert
the Public Key to hext format using the method
:py:meth:`protocoin.keys.BitcoinPublicKey.to_hex`.

Importing and Exporting Keys
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
You can also export a Private Key into the WIF (Wallet Import Format, used by
wallets to import Private Keys)::

    from protocoin import keys
    priv_key = keys.BitcoinPrivateKey()
    print priv_key.to_wif()

In this case, the output will be::

    5KWwtPkCodUs9WfbrSjzjLqnfbohABUAuLs3NpdxLqi4U6MjuKC

Which is the Private Key in the WIF format. You can also create a new Private Key
or a new Public Key using the hex representation in the construction::

    from protocoin import keys
    hex_key = "E005459416BE7FDC13FA24BA2F2C0DE289F47495D6E94CF2DFBC9FB941CBB565"
    priv_key = keys.BitcoinPrivateKey(hex_key)

If you have only the WIF format and you need to use it to create a new
Private Key, you can use the :py:meth:`protocoin.keys.BitcoinPrivateKey.from_wif`
method to import it and then create a new Private Key object like in
the example below::
    
    priv_key_wif = "5KWwtPkCodUs9WfbrSjzjLqnfbohABUAuLs3NpdxLqi4U6MjuKC"
    priv_key = BitcoinPrivateKey.from_wif(priv_key_wif)
