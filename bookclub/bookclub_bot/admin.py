from django.contrib import admin
from .models import Person, BotMessage, InviteIntent

admin.site.register(Person)
admin.site.register(BotMessage)
admin.site.register(InviteIntent)
