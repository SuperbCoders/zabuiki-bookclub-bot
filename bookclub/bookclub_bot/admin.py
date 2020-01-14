from django.contrib import admin
from .models import Person, BotMessage, InviteIntent, Location, PersonMeeting


class PersonMeetingInline(admin.StackedInline):
    model = PersonMeeting
    fk_name = 'from_person'
    can_delete = False
    fields = ('to_person', 'rate', 'review')
    readonly_fields = ('to_person', 'rate', 'review')


class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'tg_id', 'tg_username', 'username', 'location',
        'good_review', 'bad_review', 'not_met_review',
        'is_blocked'
    )
    list_filter = ('is_blocked', )
    list_per_page = 15
    inlines = [PersonMeetingInline]

    def good_review(self, person):
        return (
            PersonMeeting.objects.filter(
                from_person=person,
                rate=PersonMeeting.MeetingRate.GOOD
            ).count()
        )

    def bad_review(self, person):
        return (
            PersonMeeting.objects.filter(
                from_person=person,
                rate=PersonMeeting.MeetingRate.BAD
            ).count()
        )

    def not_met_review(self, person):
        return (
            PersonMeeting.objects.filter(
                from_person=person,
                rate=PersonMeeting.MeetingRate.NOT_MET
            ).count()
        )


admin.site.register(Person, PersonAdmin)
admin.site.register(Location)
admin.site.register(BotMessage)
admin.site.register(InviteIntent)
admin.site.register(PersonMeeting)
