from datetime import datetime

from loguru import logger
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater
from telegram import Bot, Update
from telegram.utils.request import Request

import settings


def func_logger(f):

    def inner(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"======= FUNCTION {f.__name__} STARTED AT {datetime.now()} ======")
        try:
            f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            logger.error(error_message)
            raise e
        finally:
            end_time = datetime.now() - start_time
            logger.info(f"======= FUNCTION {f.__name__} ENDED AT {datetime.now()}, EXECUTION TIME: {end_time} ======")
    return inner


@func_logger
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if chat_id in settings.ACCESSED_IDS:
        reply_text = f'Ваш ID = {chat_id}\n{text}'
        update.message.reply_text(
            text=reply_text,
        )
        if update.message["document"]:
            context.bot.send_document(chat_id=chat_id, caption="Вы отправили:", document=update.message["document"]["file_id"])
    else:
        update.message.reply_text(
            text=(
                "У вас нет доступа для использования данного бота."
                " Если это ошибка, свяжитесь с моим создателем - @MoseyJr, он что-нибудь придумает."
            ),
        )


def accessed_chat_id(chat_id: int):
    return chat_id in settings.ACCESSED_IDS


class UnavailableChatIDError(Exception):
    """
    Error raises when someone tries to send message to unavailable chat.
    """


@func_logger
def send_message_to_user(upd: Updater, chat_id: int, message: str, filebinary: str = None):
    try:
        if accessed_chat_id(chat_id):
            if filebinary:
                return upd.bot.send_document(chat_id=chat_id, caption=message, document=filebinary)
            return upd.bot.send_message(chat_id=chat_id, text=f"Вам письмо от Мо: {message}")
        else:
            raise UnavailableChatIDError(f"Chat ID #{chat_id} isn't available.")
    except UnavailableChatIDError as UCIDEx:
        logger.error(UCIDEx)


def start_bot():
    request = Request(
        connect_timeout=0.5,
        read_timeout=1.0,
        con_pool_size=8,
    )
    bot = Bot(
        request=request,
        token=settings.TELEGRAM_API_TOKEN,
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )
    send_message_to_user(updater, 355371367, "КУ, величайший!")
    send_message_to_user(updater, 3553713671, "бебебебебеб")
    send_message_to_user(updater, 309255238, "Приветствую смотрящих!", settings.FILE_BINARY)
    message_handler = MessageHandler(Filters.text, do_echo)
    file_handler = MessageHandler(Filters.document, do_echo)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(file_handler)
    updater.start_polling()
    updater.idle()
    logger.info("Telegram bot was started")


if __name__ == "__main__":
    main()

