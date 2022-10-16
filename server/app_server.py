import socket
import selectors
import traceback

from loguru import logger

from server import server_helpers
from server.settings import ConnectionSettings


class TCPServerMSS:
    sel = selectors.DefaultSelector()

    def run_TCP_server(self):
        self.init_server()
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:  # Новое подключение - необходимо принять подключение
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception as e:
                            logger.warning(
                                f"Main: Error: Exception for {message.addr}:\n"
                                f"{traceback.format_exc()}\n"
                                f"Error: {e}"
                            )
                            message.close()
        except KeyboardInterrupt:
            logger.warning("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()
        logger.info(f"Accepted connection from {addr}")
        conn.setblocking(False)  # Приняли и отключили блокировку
        message = server_helpers.Message(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def init_server(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((ConnectionSettings.HOST, ConnectionSettings.PORT))
        lsock.listen()
        logger.info("MSS SERVER WAS LAUNCHED!")
        logger.info(f"Listening on {(ConnectionSettings.HOST, ConnectionSettings.PORT)}")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)


a = TCPServerMSS()
a.run_TCP_server()





