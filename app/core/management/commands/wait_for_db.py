import time

from psycopg2 import OperationalError as Psycopg2Error

# Error Django throw when database not ready
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """command to wait for DB"""

    def handle(self, *args, **options):
        """Entrypoint"""
        self.stdout.write('Waiting for database')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                # if exception is raise, its not
                # run the rest of code in try block
                # base on self.check
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!!!!!!!'))
