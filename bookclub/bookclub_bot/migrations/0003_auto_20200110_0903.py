# Generated by Django 3.0.2 on 2020-01-10 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub_bot', '0002_inviteintent'),
    ]

    operations = [
        migrations.AddField(
            model_name='inviteintent',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='botmessage',
            name='type',
            field=models.IntegerField(choices=[(0, 'Приветствие нового пользователя'), (1, 'Обновить данные пользователя'), (2, 'Профиль сохранен'), (3, 'Не заполнены необходимые поля'), (4, 'Участвуем в следующей встрече')], primary_key=True, serialize=False, unique=True),
        ),
    ]
