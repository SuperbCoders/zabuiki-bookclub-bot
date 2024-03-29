import logging
from datetime import date, timedelta

from celery.utils.log import get_task_logger
from django.db import transaction
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized

from bookclub.celery import app
from bookclub_bot.bot import bot
from bookclub_bot.bot_handlers import want_to_party_keyboard, get_user_feedback_keyboard
from bookclub_bot.models import Person, InviteIntent, BotMessage, PersonMeeting

logger = get_task_logger(__name__)
db_logger = logging.getLogger('db_log')


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


@app.task(name='create_invite_intent', autoretry_for=(Exception,), max_retries=2)
def create_invite_intent(weekday = 0):
    today = date.today()

    # if not today.weekday() >= 5:
    #     logger.info('Must run on weekend')
    #     return

    intent_day = next_weekday(today, weekday)  # zero for monday

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
            AND a.location_id IS NOT NULL
            AND a.is_blocked = FALSE
    """)

    if persons:
        with transaction.atomic():
            InviteIntent.objects.bulk_create([
                InviteIntent(person=person, date=intent_day)
                for person in persons
            ])
        logger.info(f'Created {len(persons)} intents')
        db_logger.info(f'[{intent_day}] Создано {len(persons)} запросов на встречу')
    else:
        logger.info(f'Intents already created')
        pass
    return f'[{intent_day}] Создано {len(persons)} запросов на встречу'


@app.task(name='send_invite', autoretry_for=(Exception,), max_retries=1)
def send_invite():
    invite_text = BotMessage.objects.get(type=BotMessage.MessageTypes.INVITE)
    n = 10
    send_cnt = 0

    while True:
        intents = (
            InviteIntent.objects
                .filter(is_message_send=False, is_deleted=False)
                .order_by('person_id')
            [:n]
        )
        if not intents.exists():
            break

        for intent in intents.all():
            try:
                bot.send_message(
                    intent.person.tg_id,
                    invite_text.text,
                    reply_markup=want_to_party_keyboard
                )
            except Unauthorized as ue:
                intent.person.is_blocked = True
                intent.person.save()
                intent.delete()
                logger.error(f'Invite message wasn\'t sent for {intent.person.username}\tReason: {ue}')
            except Exception as e:
                logger.error(f'Exception for {intent.person.username} reason: {e}')
                continue
                pass
            else:
                intent.is_message_send = True
                intent.save()
                logger.info(f'Successfully sent invite message for {intent.person.username}')
                pass

            send_cnt += 1
            pass

        logger.info(f'Have sent {send_cnt} invite messages')
        pass

    db_logger.info(f'Разослано {send_cnt} сообщений')
    return f'Разослано {send_cnt} сообщений'


@app.task(name='find_pair', autoretry_for=(Exception,), max_retries=1)
def find_pair():
    # today = date.today()

    # if not today.weekday() <= 1:
    #     logger.info('Must run on week start')
    #     return

    invite_intents = InviteIntent.objects.filter(
        is_deleted=False,
        is_user_agreed=True,
        person_meeting__isnull=True
    )

    cnt = 0
    for invite_intent in invite_intents.all():

        invite_intent.refresh_from_db()
        if invite_intent.person_meeting:
            continue

        already_seen_person_ids = invite_intent.person.person_meeting.values_list('tg_id', flat=True)
        available_persons = invite_intents.exclude(person=invite_intent.person).values_list('person_id', flat=True)

        candidates = Person.objects.filter(
            location=invite_intent.person.location,
            tg_id__in=available_persons,
            is_blocked=False,
        ).exclude(
            tg_id__in=already_seen_person_ids
        )

        if not candidates.exists():
            candidates = Person.objects.filter(
                tg_id__in=available_persons,
                is_blocked=False,
            ).exclude(
                tg_id__in=already_seen_person_ids
            )

            if not candidates.exists():
                db_logger.info(f'Сочетания пар закончились для {invite_intent.person}, звать в друзья некого')
                continue

        candidate = candidates.first()

        pm = PersonMeeting.objects.create(
            from_person=invite_intent.person,
            to_person=candidate,
        )
        invite_intent.person_meeting = pm
        invite_intent.save()

        reverse_pm = PersonMeeting.objects.create(
            from_person=candidate,
            to_person=invite_intent.person,
        )
        candidate_intent = invite_intents.filter(person=candidate).get()
        candidate_intent.person_meeting = reverse_pm
        candidate_intent.save()

        cnt += 1

    db_logger.info(f'Составлено {cnt} пар')
    return f'Составлено {cnt} пар'


@app.task(name='send_pair_info', autoretry_for=(Exception,), max_retries=1)
def send_pair_info():
    msg_template = BotMessage.objects.get(type=BotMessage.MessageTypes.SEND_PAIR_INFO).text

    n = 10
    send_cnt = 0

    while True:
        pm_q = PersonMeeting.objects.filter(
            is_message_send=False
        )[:n]

        if not pm_q.exists():
            break

        for pm in pm_q.all():
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton('Написать', url=f"https://t.me/{pm.to_person.tg_username}")]
            ])
            try:
                bot.send_message(
                    pm.from_person_id,
                    msg_template.format(
                        username=pm.to_person.username,
                        about=pm.to_person.about,
                        social_networks=pm.to_person.social_networks,
                    ),
                    reply_markup=keyboard
                )
            except Unauthorized:
                pm.from_person.is_blocked = True
                pm.from_person.save()
                pm.delete()
            else:
                pm.is_message_send = True
                pm.save()

            send_cnt += 1

            logger.info(f'Send {send_cnt} invite messages')

    db_logger.info(f'Разослано {send_cnt} уведомлений о паре')


@app.task(name='send_feedback_collect', autoretry_for=(Exception,), max_retries=1)
def send_feedback_collect():
    msg_text = BotMessage.objects.get(type=BotMessage.MessageTypes.FEEDBACK_REQUEST).text
    today = date.today()

    # if not today.weekday() <= 5:
    #     logger.info('Must run on week end')
    #     return

    n = 10
    send_cnt = 0

    while True:
        pm_q = PersonMeeting.objects.filter(
            is_feedback_message_send=False
        )[:n]

        if not pm_q.exists():
            break

        for pm in pm_q.all():
            try:
                bot.send_message(
                    pm.from_person_id,
                    msg_text,
                    reply_markup=get_user_feedback_keyboard(pm.to_person_id)
                )
            except Unauthorized:
                pass
            pm.is_feedback_message_send = True
            pm.save()

            send_cnt += 1

            logger.info(f'Send {send_cnt} feedback request messages')

    db_logger.info(f'Разослано {send_cnt} запросов о фидбеке')


@app.task(name='update_meeting_schedule', autoretry_for=(Exception,), max_retries=1)
def update_meeting_schedule():
    # check if there any not send invites
    res = ""
    invite_intents = InviteIntent.objects.filter(
        is_deleted=False,
        is_message_send=False,
        person_meeting__isnull=True
    ).all()

    if not invite_intents.exists():
        res = f'No need to update db. Not sent invite intents count: {len(invite_intents)}'
        logger.info(res)
        return res

    # check if all planned meetings have taken place
    pms = PersonMeeting.objects.filter(
        is_message_send=False,
        is_feedback_message_send=False
    ).all()

    if not pms.exists():
        res = f'No need to update db. Not finished meetings count: {len(pms.all())}'
        logger.info(res)
        return res

    PersonMeeting.objects.all().delete()
    res = 'Data about meetings and invites succesfully cleared'
    logger.info(res)
    return res
