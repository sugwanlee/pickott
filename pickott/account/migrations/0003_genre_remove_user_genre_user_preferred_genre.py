# Generated by Django 4.2 on 2025-02-20 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_user_genre"),
    ]

    operations = [
        migrations.CreateModel(
            name="Genre",
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
        migrations.RemoveField(
            model_name="user",
            name="genre",
        ),
        migrations.AddField(
            model_name="user",
            name="preferred_genre",
            field=models.ManyToManyField(
                blank=True, related_name="users", to="account.genre"
            ),
        ),
    ]
