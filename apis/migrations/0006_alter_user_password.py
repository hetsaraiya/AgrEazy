# Generated by Django 5.0.6 on 2024-08-29 16:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis", "0005_alter_user_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(max_length=128, verbose_name="password"),
        ),
    ]
