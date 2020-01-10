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
        GREETING = 0, 'Приветствие нового пользователя'
        UPDATE_REGISTRATION = 1, 'Обновить данные пользователя'
        PROFILE_SAVED = 2, 'Профиль сохранен'
        FILL_REQUIRED_FIELDS = 3, 'Не заполнены необходимые поля'

    type = models.IntegerField(choices=MessageTypes.choices, unique=True, primary_key=True)
    text = models.TextField()

    def __str__(self):
        return self.MessageTypes.choices[self.type][1]
