# Generated by Django 5.0.6 on 2024-08-29 19:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis", "0011_farmerverificationdocs_satbaarcopy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="farmerverificationdocs",
            name="addhar_card",
            field=models.FileField(
                blank=True,
                null=True,
                storage="backend.supabase_storage.SupabaseStorage",
                upload_to="addhar/",
            ),
        ),
        migrations.AlterField(
            model_name="farmerverificationdocs",
            name="pan_card",
            field=models.FileField(
                blank=True,
                null=True,
                storage="backend.supabase_storage.SupabaseStorage",
                upload_to="pan-card/",
            ),
        ),
        migrations.AlterField(
            model_name="farmerverificationdocs",
            name="satbaarcopy",
            field=models.FileField(
                blank=True,
                null=True,
                storage="backend.supabase_storage.SupabaseStorage",
                upload_to="satbaarcopy/",
            ),
        ),
    ]
