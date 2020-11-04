from django.core.management.base import BaseCommand
from telegram import ext

from bookclub import settings
from bookclub_bot import bot_handlers
from bookclub_bot.bot import bot


def create(update, context):
    from bookclub_bot import tasks
    task_result = tasks.create_invite_intent()
    update.message.reply_text("create_invite_intent: ", task_result)
    pass


def send_invite(update, context):
    from bookclub_bot import tasks
    task_result = tasks.send_invite()
    update.message.reply_text("send_invite: ", task_result)
    pass


def findpair(update, context):
    from bookclub_bot import tasks
    task_result = tasks.find_pair()
    update.message.reply_text("find_pair: ", task_result)
    pass


create_handler = ext.CommandHandler('create', create)
send_handler = ext.CommandHandler('send', send_invite)
pair_handler = ext.CommandHandler('pair', findpair)


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = ext.Updater(bot=bot, use_context=True)

        dp = updater.dispatcher

        dp.add_handler(bot_handlers.start_handler)
        dp.add_handler(bot_handlers.kick_handler)
        dp.add_handler(bot_handlers.help_handler)

        dp.add_handler(bot_handlers.reg_conv_handler)

        dp.add_handler(bot_handlers.invite_intent_handler)
        dp.add_handler(bot_handlers.collect_feedback_conv_handler)

        if settings.DEBUG:
            dp.add_handler(create_handler)
            dp.add_handler(send_handler)
            dp.add_handler(pair_handler)

        updater.start_polling()
        updater.idle()
        pass
    pass
