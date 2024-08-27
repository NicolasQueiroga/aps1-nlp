import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Create a superuser, ignore if already exists"

    def handle(self, *args, **options):
        username = "nicolasmq"
        email = "nicolasqueiroga@me.com"
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR("No password found in environment variables")
            )
            return

        try:
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created superuser: {username}")
            )
        except IntegrityError:
            self.stdout.write(
                self.style.WARNING(f"Superuser {username} already exists")
            )
