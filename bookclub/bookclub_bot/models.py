from django.db import models


class Person(models.Model):
    tg_name = models.CharField(max_length=255, null=False)
    username = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    about = models.TextField()
    social_networks = models.TextField()


class BotMessage(models.Model):

    class MessageTypes(models.IntegerChoices):
        GREETING = 0, 'Приветствие нового пользователя'

    type = models.IntegerField(choices=MessageTypes.choices, unique=True, primary_key=True)
    text = models.TextField()

    def __str__(self):
        return self.MessageTypes.choices[self.type][1]
