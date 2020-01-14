from django.contrib import admin
from .models import Person, BotMessage, InviteIntent, Location, PersonMeeting

admin.site.register(Person)
admin.site.register(Location)
admin.site.register(BotMessage)
admin.site.register(InviteIntent)
admin.site.register(PersonMeeting)
