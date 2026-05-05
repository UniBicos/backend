import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update a seeded superuser account."

    def add_arguments(self, parser):
        parser.add_argument("--email", default=os.getenv("SEED_SUPERUSER_EMAIL"))
        parser.add_argument("--password", default=os.getenv("SEED_SUPERUSER_PASSWORD"))
        parser.add_argument("--nome", default=os.getenv("SEED_SUPERUSER_NOME"))
        parser.add_argument("--telefone", default=os.getenv("SEED_SUPERUSER_TELEFONE"))

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        nome = options["nome"]
        telefone = options["telefone"]

        missing = [
            label
            for label, value in (
                ("email", email),
                ("password", password),
                ("nome", nome),
                ("telefone", telefone),
            )
            if not value
        ]
        if missing:
            raise CommandError(
                "Missing required values: " + ", ".join(missing) + ". "
                "Pass them as command options or set the SEED_SUPERUSER_* environment variables."
            )

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            email=email,
            defaults={
                "nome": nome,
                "telefone": telefone,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.nome = nome
        user.telefone = telefone
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} superuser {user.email} (id={user.pk})."))
