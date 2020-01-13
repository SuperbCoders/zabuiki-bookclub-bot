from django.db import models


class Person(models.Model):
    tg_id = models.IntegerField(null=False, unique=True)
    username = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    about = models.TextField()
    social_networks = models.TextField()

    def __str__(self):
        return f"{self.tg_id} - {self.username} - {self.city}"


class BotMessage(models.Model):

    class MessageTypes(models.IntegerChoices):
        REG_WELCOME = 0, 'Пользователь начинает регистрацию'
        UPDATE_REGISTRATION = 1, 'Обновить данные пользователя'
        PROFILE_SAVED = 2, 'Профиль сохранен'
        FILL_REQUIRED_FIELDS = 3, 'Не заполнены необходимые поля'

        INVITE = 4, 'Участвуем в следующей рассылке'
        INVITE_CONFIRMED = 5, 'Человек подтвердил участие в рассылке'
        INVITE_DECLINED = 6, 'Человек отказался от участия в рассылке'

        USER_WELCOME = 7, 'Приветсвие пользователя'

    type = models.IntegerField(choices=MessageTypes.choices, unique=True, primary_key=True)
    text = models.TextField()

    def __str__(self):
        return self.MessageTypes.choices[self.type][1]


class InviteIntent(models.Model):
    date = models.DateField()
    person = models.ForeignKey(Person, to_field='tg_id', on_delete=models.CASCADE)

    is_message_send = models.BooleanField(default=False)
    is_user_agreed = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['date', 'person']

    def __str__(self):
        return f"{self.date} - {self.person_id}"
