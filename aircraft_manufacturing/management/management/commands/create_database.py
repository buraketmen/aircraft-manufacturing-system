from django.core.management.base import BaseCommand
from django.conf import settings
from psycopg2 import connect, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Command(BaseCommand):
    help = 'Create PostgreSQL database if it does not exist'

    def handle(self, *args, **kwargs):
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings.get('PORT', '5432')

        conn = connect(
            dbname='postgres',
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [db_name])
        exists = cursor.fetchone()
        if not exists:
            self.stdout.write(self.style.NOTICE(f"Database {db_name} does not exist. Creating..."))
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            self.stdout.write(self.style.SUCCESS(f"Database {db_name} created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Database {db_name} already exists."))

        cursor.close()
        conn.close()
