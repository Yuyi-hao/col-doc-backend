# Generated by Django 5.1.4 on 2024-12-09 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='tc',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
