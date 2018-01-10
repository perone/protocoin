Changelog
===============================================================================
In this section you'll find information about what's new in the newer
releases of the project.

Release v.0.3
-------------------------------------------------------------------------------

    * Improved support for displaying services advertised by version negotiation (thanks to `@jhart-r7 <https://github.com/jhart-r7>`_);

Release v.0.2
-------------------------------------------------------------------------------

    * Fixed a bug when the nodes were disconnecting;
    * Implemented the GetAddr message command;
    * Added the key/address management module;
    * Added the utility module;
    * Added a new example: creation of a brain wallet;
    * Rewrite of the socket recv loop;
    * Fixed a bug in the socket closing;
    * Improved the send_message() of the BitcoinBasicClient;
    * Fixed protocol support for TxIn sequence (thanks to `@bmuller <https://github.com/bmuller>`_);
    * Refactoring to add SerializableMessage class (thanks to `@bmuller <https://github.com/bmuller>`_);
    * Fixed a bug in BitcoinPublicKey class (thanks to `@bmuller <https://github.com/bmuller>`_);

Release v.0.1
-------------------------------------------------------------------------------
This is the first release of the project. Some messages of the protocol are
still missing and will be implemented in the next versions, the list of features
implemented in this release are:

    * Documentation
    * Field Types
        * Base classes
        * Int32LEField
        * UInt32LEField
        * Int64LEField
        * UInt64LEField
        * Int16LEField
        * UInt16LEField
        * UInt16BEField
        * FixedStringField
        * NestedField
        * ListField
        * IPv4AddressField
        * VariableIntegerField
        * VariableStringField
        * Hash
    * Serializers
        * Base classes, metaclasses
        * MessageHeaderSerializer
        * IPv4AddressSerializer
        * IPv4AddressTimestampSerializer
        * VersionSerializer
        * VerAckSerializer
        * PingSerializer
        * PongSerializer
        * InventorySerializer
        * InventoryVectorSerializer
        * AddressVectorSerializer
        * GetDataSerializer
        * NotFoundSerializer
        * OutPointSerializer
        * TxInSerializer
        * TxOutSerializer
        * TxSerializer
        * BlockHeaderSerializer
        * BlockSerializer
        * HeaderVectorSerializer
        * MemPoolSerializer
    * Clients
        * BitcoinBasicClient
        * BitcoinClient


