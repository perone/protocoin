
class NodeDisconnectException(Exception):
    """This exception is thrown when Protocoin detects a
    disconnection from the node it is connected."""
    pass


class InvalidMessageChecksum(Exception):
    """This exception is thrown when the checksum for a
    message in a message header doesn't match the actual
    checksum of the message."""
    pass

