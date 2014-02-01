from cStringIO import StringIO
from .serializers import *
from .exceptions import NodeDisconnectException
import os

class BitcoinBasicClient(object):
    """The base class for a Bitcoin network client, this class
    implements utility functions to create your own class.

    :param socket: a socket that supports the makefile()
                   method.
    """

    coin = "bitcoin"

    def __init__(self, socket):
        self.socket = socket
        self.buffer = StringIO()

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

    def handle_send_message(self, message_header, message):
        """This method will be called for every sent message.

        :param message_header: The header of the message
        :param message: The message to be sent
        """
        pass

    def receive_message(self):
        """This method is called inside the loop() method to
        receive a message from the stream (socket) and then
        deserialize it."""

        # Calculate the size of the buffer
        self.buffer.seek(0, os.SEEK_END)
        buffer_size = self.buffer.tell()

        # Check if a complete header is present
        if buffer_size < MessageHeaderSerializer.calcsize():
            return

        # Go to the beginning of the buffer
        self.buffer.reset()

        message_model = None
        message_header_serial = MessageHeaderSerializer()
        message_header = message_header_serial.deserialize(self.buffer)

        total_length = MessageHeaderSerializer.calcsize() + message_header.length

        # Incomplete message
        if buffer_size < total_length:
            self.buffer.seek(0, os.SEEK_END)
            return

        payload = self.buffer.read(message_header.length)
        self.buffer = StringIO()
        self.handle_message_header(message_header, payload)

        payload_checksum = \
            MessageHeaderSerializer.calc_checksum(payload)

        # Check if the checksum is valid
        if payload_checksum != message_header.checksum:
            return (message_header, message_model)

        if message_header.command in MESSAGE_MAPPING:
            deserializer = MESSAGE_MAPPING[message_header.command]()
            message_model = deserializer.deserialize(StringIO(payload))

        return (message_header, message_model)

    def send_message(self, message, serializer):
        """This method will serialize the message using the
        specified serializer and then it will send it
        to the socket stream.

        :param message: The message object to send
        :param serializer: The serializar of the message
        """
        bin_data = StringIO()
        message_header = MessageHeader(self.coin)
        message_header_serial = MessageHeaderSerializer()

        bin_message = serializer.serialize(message)
        payload_checksum = \
            MessageHeaderSerializer.calc_checksum(bin_message)
        message_header.checksum = payload_checksum
        message_header.length = len(bin_message)
        message_header.command = message.command

        bin_data.write(message_header_serial.serialize(message_header))
        bin_data.write(bin_message)

        self.socket.sendall(bin_data.getvalue())
        self.handle_send_message(message_header, message)

    def loop(self):
        """This is the main method of the client, it will enter
        in a receive/send loop."""

        while True:
            data = self.socket.recv(1024*8)

            if len(data) <= 0:
                raise NodeDisconnectException("Node disconnected.")
            
            self.buffer.write(data)
            data = self.receive_message()

            # Check if the message is still incomplete to parse
            if data is None:
                continue

            # Check for the header and message
            message_header, message = data
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
        version_serial = VersionSerializer()
        self.send_message(version, version_serial)

    def handle_version(self, message_header, message):
        """This method will handle the Version message and
        will send a VerAck message when it receives the
        Version message.

        :param message_header: The Version message header
        :param message: The Version message
        """
        verack = VerAck()
        verack_serial = VerAckSerializer()
        self.send_message(verack, verack_serial)

    def handle_ping(self, message_header, message):
        """This method will handle the Ping message and then
        will answer every Ping message with a Pong message
        using the nonce received.

        :param message_header: The header of the Ping message
        :param message: The Ping message
        """
        pong = Pong()
        pong_serial = PongSerializer()
        pong.nonce = message.nonce
        self.send_message(pong, pong_serial)
