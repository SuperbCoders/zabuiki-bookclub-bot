from django.core.management.base import BaseCommand

from bookclub_bot.models import BotMessage


class Command(BaseCommand):
    DEFAULT_TEXTS = {
        BotMessage.MessageTypes.USER_WELCOME: 'Привет! Я бот для встреч клуба, зарегестрируйся с помощью команды /register',
        BotMessage.MessageTypes.REG_WELCOME: 'Привет! Начнем регистрацию',
        BotMessage.MessageTypes.UPDATE_REGISTRATION: 'Обновить данные профиля',
        BotMessage.MessageTypes.PROFILE_SAVED: 'Ваш профиль сохранен',
        BotMessage.MessageTypes.FILL_REQUIRED_FIELDS: 'Город должен быть обязательно заполнен',
        BotMessage.MessageTypes.INVITE: 'Участвуете во встрече на следующей неделе?',
        BotMessage.MessageTypes.INVITE_CONFIRMED: 'Вы участвуете в составлении пар на следующую неделю',
        BotMessage.MessageTypes.INVITE_DECLINED: 'Вы отказались от встречи на следующую неделю',
    }

    def handle(self, *args, **options):
        for msg_type, msg_text in self.DEFAULT_TEXTS.items():
            if not BotMessage.objects.filter(type=msg_type).exists():
                BotMessage.objects.create(
                    type=msg_type,
                    text=msg_text
                )
