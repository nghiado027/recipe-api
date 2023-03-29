"""
Test custom command Django managment
"""

# to mock behavior of database (simulate, not actual database)
# to return response or not
from unittest.mock import patch

# possibilities errors might get when try to connect database b4 ready
from psycopg2 import OperationalError as Psycopg2Error

# helper function to call command by name (use for testing)
from django.core.management import call_command

# get operation error to throw exception from database
from django.db.utils import OperationalError

# for simple testing
from django.test import SimpleTestCase

# Command going tobe mocking wait_for_db (in commands folder)
# ".check" base on BaseCommand (check wait_for_db.py file, class Command)
# for return exception, value,.. also simulate


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    # patched_check take ".check" return value from @patch decorator
    # simplify get the argument from decorator patch
    def test_wait_for_database_ready(self, patched_check):
        """Test waiting database if it ready"""
        patched_check.return_value = True

        call_command('wait_for_db')

        # Check if check method is called with "database=['default']"
        # docker-compose run --rm app sh -c "python manage.py test" to test
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_database_delay(self, patched_sleep, patched_check):
        """Test wait database when get OperationalError"""

        # Use "".side_effect" to handle
        # deffierent type (raise exception instead of get value)
        # define various different value everytime we call
        # "*2" to get 2 times Psycopg2Error errror and 3 times OperationalError
        # After that  the sixth time we call it, get the true back
        # get return instead of erasing as an exception value
        patched_check.side_effect = [Psycopg2Error] * 2 \
            + [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        # Check
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
