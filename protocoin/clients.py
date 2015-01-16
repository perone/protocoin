from cStringIO import StringIO
from .serializers import *
from .exceptions import NodeDisconnectException
import os


class ProtocolBuffer(object):
    def __init__(self):
        self.buffer = StringIO()
        self.header_size = MessageHeaderSerializer.calcsize()

    def write(self, data):
        self.buffer.write(data)

    def receive_message(self):
        """This method will attempt to extract a header and message.
        It will return a tuple of (header, message) and set whichever
        can be set so far (None otherwise).
        """
        # Calculate the size of the buffer
        self.buffer.seek(0, os.SEEK_END)
        buffer_size = self.buffer.tell()

        # Check if a complete header is present
        if buffer_size < self.header_size:
            return (None, None)

        # Go to the beginning of the buffer
        self.buffer.reset()

        message_model = None
        message_header_serial = MessageHeaderSerializer()
        message_header = message_header_serial.deserialize(self.buffer)
        total_length = self.header_size + message_header.length

        # Incomplete message
        if buffer_size < total_length:
            self.buffer.seek(0, os.SEEK_END)
            return (message_header, None)

        payload = self.buffer.read(message_header.length)
        remaining = self.buffer.read()
        self.buffer = StringIO()
        self.buffer.write(remaining)
        payload_checksum = MessageHeaderSerializer.calc_checksum(payload)

        # Check if the checksum is valid
        if payload_checksum != message_header.checksum:
            raise RuntimeError("Bad message checksum")

        if message_header.command in MESSAGE_MAPPING:
            deserializer = MESSAGE_MAPPING[message_header.command]()
            message_model = deserializer.deserialize(StringIO(payload))

        return (message_header, message_model)

class BitcoinBasicClient(object):
    """The base class for a Bitcoin network client, this class
    implements utility functions to create your own class.

    :param socket: a socket that supports the makefile()
                   method.
    """

    coin = "bitcoin"

    def __init__(self, socket):
        self.socket = socket
        self.buffer = ProtocolBuffer()

    def close_stream(self):
        """This method will close the socket stream."""
        self.socket.close()

    def handle_message_header(self, message_header, payload):
        """This method will be called for every message before the
        message payload deserialization.

        :param message_header: The message header
        :param payload: The payload of the message
        """
        pass

    def send_message(self, message):
        """This method will serialize the message using the
        appropriate serializer based on the message command
        and then it will send it to the socket stream.

        :param message: The message object to send
        """
        self.socket.sendall(message.get_message(self.coin))

    def loop(self):
        """This is the main method of the client, it will enter
        in a receive/send loop."""

        while True:
            data = self.socket.recv(1024*8)

            if len(data) <= 0:
                raise NodeDisconnectException("Node disconnected.")
            
            self.buffer.write(data)
            message_header, message = self.buffer.receive_message()

            if message_header is not None:
                self.handle_message_header(message_header, data)

            if not message:
                continue

            handle_func_name = "handle_" + message_header.command
            handle_func = getattr(self, handle_func_name, None)
            if handle_func:
                handle_func(message_header, message)

class BitcoinClient(BitcoinBasicClient):
    """This class implements all the protocol rules needed
    for a client to stay up in the network. It will handle
    the handshake rules as well answer the ping messages."""

    def handshake(self):
        """This method will implement the handshake of the
        Bitcoin protocol. It will send the Version message."""
        version = Version()
        self.send_message(version)

    def handle_version(self, message_header, message):
        """This method will handle the Version message and
        will send a VerAck message when it receives the
        Version message.

        :param message_header: The Version message header
        :param message: The Version message
        """
        verack = VerAck()
        self.send_message(verack)

    def handle_ping(self, message_header, message):
        """This method will handle the Ping message and then
        will answer every Ping message with a Pong message
        using the nonce received.

        :param message_header: The header of the Ping message
        :param message: The Ping message
        """
        pong = Pong()
        pong.nonce = message.nonce
        self.send_message(pong)
