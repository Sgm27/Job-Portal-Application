# Generated by Django 5.1.7 on 2025-03-25 03:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
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
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("requirements", models.TextField()),
                ("location", models.CharField(max_length=100)),
                ("salary", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "job_type",
                    models.CharField(
                        choices=[
                            ("full_time", "Full Time"),
                            ("part_time", "Part Time"),
                            ("contract", "Contract"),
                            ("internship", "Internship"),
                            ("remote", "Remote"),
                        ],
                        default="full_time",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("application_deadline", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("filled", "Filled"),
                            ("expired", "Expired"),
                            ("draft", "Draft"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                (
                    "employer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Application",
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
                ("cover_letter", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("reviewed", "Reviewed"),
                            ("shortlisted", "Shortlisted"),
                            ("rejected", "Rejected"),
                            ("hired", "Hired"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="jobs.job",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("job", "applicant")},
            },
        ),
    ]
