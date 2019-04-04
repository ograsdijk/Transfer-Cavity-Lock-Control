import sys
import socket
import selectors
import traceback
import threading
from collections import deque
import random
import logging
import time

from ServerMessage import ServerMessage

class SocketDeviceServer:
    """
    SocketDeviceServer template class for easy setup of specific device classes
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.sock.setblocking(False)
        self.sel = selectors.DefaultSelector()

        self.sel.register(self.sock, selectors.EVENT_READ, data=None)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        logging.info("SocketDeviceServer accepted connection from", addr)
        conn.setblocking(False)
        message = ServerMessage(self.sel, conn, addr, self.data,
                                self.create_response)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def run(self):
        try:
            self.device.start()
            while True:
                
                events = self.sel.select(timeout = None)

                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception as err:
                            logging.warning("SocketDeviceServer warning for "
                                           +"{0}:{1} : ".format(self.host, self.port)
                                           +str(err))
                            message.close()
        except KeyboardInterrupt:
            logging.warning("SocketDevice server warning : KeyboardInterrupt, \
                             exiting")
        finally:
            self.sel.close()
