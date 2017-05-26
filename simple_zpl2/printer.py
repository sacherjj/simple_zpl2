import socket
from .formatter import Formatter


class NetworkPrinter(object):
    """
    Object to send ZPL to zebra network printer using sockets
    """

    def __init__(self, ip_address, port=9100):
        self.ip = ip_address
        self.port = port

    def print(self, label_formatter: Formatter, timeout=10):
        """
        Send ZPL2 formatted text to a network label printer
        
        :param label_formatter: Formatter object, fully build for label.
        :return: None
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((self.ip, self.port))
            s.send(label_formatter.zpl_data)
