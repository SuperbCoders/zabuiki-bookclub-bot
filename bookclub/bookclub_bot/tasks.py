from datetime import date, timedelta

from celery.utils.log import get_task_logger
from django.db import transaction
from telegram import ReplyKeyboardMarkup

from bookclub.celery import app
from bookclub_bot.bot import bot
from bookclub_bot.models import Person, InviteIntent, BotMessage

logger = get_task_logger(__name__)


@app.task(name='create_invite_intent', autoretry_for=(Exception,), max_retries=2)
def create_invite_intent():
    today = date.today()
    # assert today.weekday() >= 5, 'script must run at week end'

    intent_day = today + timedelta((0 - today.weekday()) % 7)  # zero for monday

    # disable previous intents
    prev_intent_day = intent_day - timedelta(days=7)
    (
        InviteIntent.objects.filter(
            date__lte=prev_intent_day,
            is_deleted=False,
        ).update(is_deleted=True)
    )

    persons = Person.objects.raw(f"""
        SELECT a.*
        FROM bookclub_bot_person AS a
        LEFT JOIN (
            SELECT *
            FROM bookclub_bot_inviteintent
            WHERE date = '{intent_day}'
        ) AS b ON a.tg_id = b.person_id
        WHERE b.person_id IS NULL
            AND a.tg_id IS NOT NULL
            AND a.city IS NOT NULL
    """)

    if persons:
        with transaction.atomic():
            InviteIntent.objects.bulk_create([
                InviteIntent(person=person, date=intent_day)
                for person in persons
            ])
        logger.info(f'Created {len(persons)} intents')
    else:
        logger.info(f'Intents already created')


@app.task(name='send_invite', autoretry_for=(Exception,), max_retries=1)
def send_invite():
    invite_text = BotMessage.objects.get(type=BotMessage.MessageTypes.INVITE)
    markup = ReplyKeyboardMarkup([['Участвую', 'Не участвую']], resize_keyboard=True, one_time_keyboard=True)
    n = 10

    while True:
        with transaction.atomic():
            intents = (
                InviteIntent.objects
                    .filter(is_message_send=False, is_deleted=False)
                    .order_by('person_id')
                    .select_for_update(skip_locked=True)
                [:n]
            )
            if not intents.exists():
                break

            for intent in intents.all():
                bot.send_message(
                    intent.person_id,
                    invite_text.text,
                    reply_markup=markup
                )
                intent.is_message_send = True
                intent.save()
