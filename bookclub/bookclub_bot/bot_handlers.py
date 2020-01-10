from collections import OrderedDict

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from bookclub_bot.models import BotMessage, Person, InviteIntent

#
# User registration
#

CHOOSING, TYPING_REPLY = range(2)
PERSON_PROPERTY_MAPPINGS = OrderedDict(
    (("Имя", "username"), ("Город", "city"), ("О себе", "about"), ("Социальные сети", "social_networks"),)
)
DONE_WORD = "Готово"


def get_reply_keyboard():
    verbose_names = list(PERSON_PROPERTY_MAPPINGS.keys())
    n = 2
    reply_keyboard = [verbose_names[i: i + n] for i in range(0, len(verbose_names), n)] + [[DONE_WORD]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    return markup


def facts_to_str(user_obj):
    facts = list()

    for verbose_name, property in PERSON_PROPERTY_MAPPINGS.items():
        facts.append("{} - {}".format(verbose_name, getattr(user_obj, property)))

    return "\n".join(facts).join(["\n", "\n"])


def start(update, context):
    user, created = Person.objects.get_or_create(
        tg_id=update.effective_user.id,
    )

    if not created:
        greeting_text = BotMessage.objects.get(type=BotMessage.MessageTypes.UPDATE_REGISTRATION).text
    else:
        greeting_text = BotMessage.objects.get(type=BotMessage.MessageTypes.GREETING).text

        user.username = update.effective_user.first_name
        user.save()

    greeting_text += facts_to_str(user)
    update.message.reply_text(greeting_text, reply_markup=get_reply_keyboard())
    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data["choice"] = PERSON_PROPERTY_MAPPINGS[text]
    update.message.reply_text(f"Итак, {text.lower()}:")

    return TYPING_REPLY


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text

    category = user_data["choice"]
    del user_data["choice"]
    user = Person.objects.get(tg_id=update.effective_user.id)
    setattr(user, category, text)
    user.save()

    update.message.reply_text(
        "Сохранено! Ваш профиль:" "{}" "".format(facts_to_str(user)), reply_markup=get_reply_keyboard()
    )

    return CHOOSING


def done(update, context):
    user = Person.objects.get(tg_id=update.effective_user.id)
    if not user.city:
        text_obj = BotMessage.objects.get(type=BotMessage.MessageTypes.FILL_REQUIRED_FIELDS)
        update.message.reply_text(
            f"{text_obj.text}\n {facts_to_str(user)}",
            reply_markup=get_reply_keyboard()
        )

        return CHOOSING

    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    text_obj = BotMessage.objects.get(type=BotMessage.MessageTypes.PROFILE_SAVED)
    update.message.reply_text(text_obj.text)

    user_data.clear()
    return ConversationHandler.END


reg_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("register", start)],
    states={
        CHOOSING: [MessageHandler(Filters.regex(f'^({"|".join(PERSON_PROPERTY_MAPPINGS.keys())})$'), regular_choice), ],
        TYPING_REPLY: [MessageHandler(Filters.text, received_information), ],
    },
    fallbacks=[MessageHandler(Filters.regex(f"^{DONE_WORD}"), done)],
)

#
# Invite intent handling
#


def set_invite_intent(update, context):
    q = InviteIntent.objects.filter(
        person_id=update.effective_user.id,
        is_deleted=False,
    )
    if update.message.text == 'Участвую':
        q.update(is_user_agreed=True)
        reply_text = BotMessage.objects.get(type=BotMessage.MessageTypes.INVITE_CONFIRMED).text
    else:
        q.update(is_user_agreed=False)
        reply_text = BotMessage.objects.get(type=BotMessage.MessageTypes.INVITE_DECLINED).text

    update.message.reply_text(reply_text)


invite_intent_handler = MessageHandler(Filters.regex(f"^(Участвую|Не участвую)$"), set_invite_intent)