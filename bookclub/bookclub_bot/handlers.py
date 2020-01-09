from telegram.ext import ConversationHandler, CommandHandler
from bookclub_bot.models import BotMessage

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    greeting_text = BotMessage.objects.get(type=BotMessage.MessageTypes.GREETING)
    update.message.reply_text(greeting_text.text)
    return CHOOSING


register_handler = CommandHandler('register', start)