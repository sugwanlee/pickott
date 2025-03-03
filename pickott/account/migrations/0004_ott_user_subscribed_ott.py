# Generated by Django 4.2 on 2025-02-23 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_genre_remove_user_genre_user_preferred_genre"),
    ]

    operations = [
        migrations.CreateModel(
            name="Ott",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="subscribed_ott",
            field=models.ManyToManyField(
                blank=True, related_name="otts", to="account.ott"
            ),
        ),
    ]
