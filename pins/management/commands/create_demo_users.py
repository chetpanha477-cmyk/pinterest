from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create demo users (idempotent - safe to run every deploy)"

    def handle(self, *args, **options):
        users = [
            ("demo", "demo12345", True),      # (username, password, is_superuser)
            ("sophea", "sophea123", False),
            ("dara", "dara12345", False),
            ("mealea", "mealea123", False),
        ]

        for username, password, is_super in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )
            user.set_password(password)
            user.is_staff = is_super
            user.is_superuser = is_super
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated existing user: {username}"))
