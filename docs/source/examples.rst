Examples
===============================================================================
In this section you can see various examples using Protocoin API.

Receiving blocks in real-time
--------------------------------------------------------------------------------
In this example we will print the block information as well the block hash
when blocks arrive in real-time from the nodes. It will also print the
name of each message received::

	import socket
	from protocoin.clients import *

	class MyBitcoinClient(BitcoinClient):
	    def handle_block(self, message_header, message):
	        print message
	        print "Block hash:", message.calculate_hash()

	    def handle_inv(self, message_header, message):
	        getdata = GetData()
	        getdata_serial = GetDataSerializer()
	        getdata.inventory = message.inventory
	        self.send_message(getdata, getdata_serial)

	    def handle_message_header(self, message_header, payload):
	        print "Received message:", message_header.command

	    def handle_send_message(self, message_header, message):
	        print "Message sent:", message_header.command

	def run_main():
	    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    sock.connect(("bitcoin.sipa.be", 8333))
	    client = MyBitcoinClient(sock)
	    client.handshake()
	    client.loop()

The example above will output::

	<Block Version=[2] Timestamp=[Fri Nov 22 13:58:59 2013] Nonce=[1719395575] Hash=[0000000000000004b798ea6eb896bb3d39f1f1b19d285a0d48167e8661387e58] Tx Count=[232]>
	Block hash: 0000000000000004b798ea6eb896bb3d39f1f1b19d285a0d48167e8661387e58

Note that in the example above, the **handle_inv** was implemented in order to
retrieve the inventory data using the GetData message command. Without the GetData
command, we only receive the Inv message command.

Inspecting transactions output
--------------------------------------------------------------------------------
In the example below we're showing the output value in BTCs for each transaction
output::

	import socket
	from protocoin.clients import *

	class MyBitcoinClient(BitcoinClient):
	    def handle_tx(self, message_header, message):
	        print message
	        for tx_out in message.tx_out:
	            print "BTC: %.8f" % tx_out.get_btc_value()

	    def handle_inv(self, message_header, message):
	        getdata = GetData()
	        getdata_serial = GetDataSerializer()
	        getdata.inventory = message.inventory
	        self.send_message(getdata, getdata_serial)

	def run_main():
	    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    sock.connect(("bitcoin.sipa.be", 8333))
	    print "Connected !"
	    client = MyBitcoinClient(sock)
	    client.handshake()
	    client.loop()

	if __name__ == "__main__":
	    run_main()

The example above will show the following output for every transaction, in this
example it is showing a transaction with 13 inputs and 2 outputs of 0.25 BTC and
0.00936411 BTC::

	<Tx Version=[1] Lock Time=[Always Locked] TxIn Count=[13] TxOut Count=[2]>
	BTC: 0.25000000
	BTC: 0.00936411