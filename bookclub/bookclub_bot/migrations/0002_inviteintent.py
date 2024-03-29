# Generated by Django 3.0.2 on 2020-01-10 06:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookclub_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteIntent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_message_send', models.BooleanField(default=False)),
                ('is_user_agreed', models.BooleanField(default=False)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclub_bot.Person', to_field='tg_id')),
            ],
            options={
                'unique_together': {('date', 'person')},
            },
        ),
    ]
