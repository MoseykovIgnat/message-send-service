from server.app_server import TCPServerMSS
from telegram_sender.bot import start_bot


def initialize_service():
    server = TCPServerMSS()
    server.run_TCP_server()
    start_bot()


if __name__ == '__main__':
    initialize_service()
    # Сюда хенделры!