import socket


class NetworkPrinter(object):
    """
    Object to send ZPL to zebra network printer using sockets

    :param ip_address: printer network address as 'xxx.xxx.xxx.xxx'
    :param port: port of printer as int (default 9100)
    """

    def __init__(self, ip_address, port=9100):
        self.ip = ip_address
        self.port = port

    def print_zpl(self, zpl_document, timeout=10):
        """
        Send ZPL2 formatted text to a network label printer

        :param zpl_document: Document object, fully build for label.
        :param timeout: Socket timeout for printer connection, default 10.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((self.ip, self.port))
            s.send(zpl_document.zpl_bytes)
