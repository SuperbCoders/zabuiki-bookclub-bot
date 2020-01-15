from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class BookclubEntitiesConfig(AppConfig):
    name = 'bookclub_bot'


class BookclubAdminConfig(AdminConfig):
    default_site = 'bookclub_bot.admin.BookclubAdminSite'
