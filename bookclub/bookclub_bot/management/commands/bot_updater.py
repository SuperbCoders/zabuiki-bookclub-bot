from django.core.management.base import BaseCommand
from telegram import ext

from bookclub_bot import handlers
from bookclub_bot.bot import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = ext.Updater(bot=bot, use_context=True)

        dp = updater.dispatcher

        dp.add_handler(handlers.register_handler)

        updater.start_polling()
        updater.idle()
