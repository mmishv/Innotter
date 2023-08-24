# Generated by Django 4.2.4 on 2023-08-24 06:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Page",
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
                ("name", models.CharField(max_length=80)),
                ("uuid", models.CharField(max_length=36, unique=True)),
                ("description", models.TextField()),
                ("owner_uuid", models.CharField(max_length=36)),
                ("image_s3_path", models.CharField(blank=True)),
                ("is_private", models.BooleanField(default=False)),
                ("unblock_date", models.DateTimeField(blank=True, null=True)),
                ("tags", models.ManyToManyField(related_name="pages", to="pages.tag")),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="PageRequest",
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
                ("requester_uuid", models.CharField(max_length=36)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="follow_requests",
                        to="pages.page",
                    ),
                ),
            ],
            options={
                "unique_together": {("page", "requester_uuid")},
            },
        ),
        migrations.CreateModel(
            name="PageFollower",
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
                ("follower_uuid", models.CharField(max_length=36)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="followers",
                        to="pages.page",
                    ),
                ),
            ],
            options={
                "unique_together": {("page", "follower_uuid")},
            },
        ),
    ]
