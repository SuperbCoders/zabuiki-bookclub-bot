from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Person(models.Model):
    tg_id = models.IntegerField(null=False, unique=True)
    username = models.CharField(max_length=255)
    location = models.ForeignKey(Location, null=True, on_delete=models.CASCADE)
    about = models.TextField()
    social_networks = models.TextField()

    def __str__(self):
        return f"{self.tg_id} - {self.username} - {self.location}"


class BotMessage(models.Model):

    class MessageTypes(models.IntegerChoices):
        USER_WELCOME = 0, 'Приветсвие пользователя'

        ASK_FOR_NAME = 1, 'Спрашиваем имя'
        ASK_FOR_ABOUT = 2, 'Спрашиваем о себе'
        ASK_FOR_SOCIAL = 3, 'Спрашиваем соц сети'
        ASK_FOR_CITY = 4, 'Спрашиваем город'

        PROFILE_SAVED = 5, 'Профиль сохранен'

        INVITE = 6, 'Участвуем в следующей рассылке'
        INVITE_CONFIRMED = 7, 'Человек подтвердил участие в рассылке'
        INVITE_DECLINED = 8, 'Человек отказался от участия в рассылке'

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
