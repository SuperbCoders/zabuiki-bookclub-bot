from django.core.management.base import BaseCommand
from telegram import ext

from bookclub_bot import bot_handlers
from bookclub_bot.bot import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = ext.Updater(bot=bot, use_context=True)

        dp = updater.dispatcher

        dp.add_handler(bot_handlers.start_handler)
        dp.add_handler(bot_handlers.reg_conv_handler)
        dp.add_handler(bot_handlers.invite_intent_handler)

        updater.start_polling()
        updater.idle()
