from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Cleans all migrations: deletes migration files and clears django_migrations table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all Django apps
        django_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
        
        # Clear django_migrations table if exist in database
        with connection.cursor() as cursor:
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    "Would delete all records from django_migrations table"
                ))
            else:
                try:
                    cursor.execute("DELETE FROM django_migrations;")
                    self.stdout.write(self.style.SUCCESS(
                        "Cleared django_migrations table"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error clearing django_migrations table: {e}"
                    ))

        # Delete migration files from all apps
        for app in django_apps:
            app_path = app.replace('.', '/')
            migrations_path = os.path.join(settings.BASE_DIR, app_path, 'migrations')
            
            if os.path.exists(migrations_path):
                for filename in os.listdir(migrations_path):
                    if filename.endswith('.py') and filename != '__init__.py':
                        file_path = os.path.join(migrations_path, filename)
                        if dry_run:
                            self.stdout.write(self.style.WARNING(
                                f"Would delete migration file: {file_path}"
                            ))
                        else:
                            os.remove(file_path)
                            self.stdout.write(self.style.SUCCESS(
                                f"Deleted migration file: {file_path}"
                            ))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                "\nDry run completed. Use without --dry-run to actually delete files."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "\nMigrations cleaned successfully. Now you can run:"
                "\n1. python manage.py makemigrations"
                "\n2. python manage.py migrate"
            )) 