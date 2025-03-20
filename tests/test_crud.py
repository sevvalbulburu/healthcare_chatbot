# Unit tests for database creation and database processes 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, time
from database import create_booking_table, cursor, connection
from crud import (
    add_appointment,
    get_patient_info,
    get_all_appointments,
    get_appointment_by_id,
    update_appointment,
    delete_appointment,
)

class TestDatabaseOperations(unittest.TestCase):
    
    @patch('crud.cursor')
    @patch('crud.connection')
    def test_add_appointment(self, mock_connection, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_connection.commit = MagicMock()

        # Call the function
        add_appointment('John', 'Doe', '12345', date(2025, 3, 15), time(10, 30), 'Checkup')

        # Assert that execute was called with the expected query and values
        expected_query = "INSERT INTO appointments (name, surname, personal_id, date, time, description) VALUES (?, ?, ?, ?, ?, ?)",('John', 'Doe', '12345', date(2025, 3, 15), time(10, 30), 'Checkup')
        mock_cursor.execute.assert_called_once_with(expected_query)
        mock_connection.commit.assert_called_once()

    @patch('crud.cursor')
    def test_get_patient_info(self, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_cursor.fetchall = MagicMock(return_value=[('John', 'Doe', '12345', date(2025, 3, 15), time(10, 30), 'Checkup')])

        # Call the function
        get_patient_info('12345')

        # Assert that execute was called with the expected query and personal_id
        mock_cursor.execute.assert_called_once_with(
            ("SELECT * FROM appointments WHERE personal_id = ?", '12345')
        )

    @patch('crud.cursor')
    def test_get_all_appointments(self, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_cursor.fetchall = MagicMock(return_value=[('John', 'Doe', '12345', date(2025, 3, 15), time(10, 30), 'Checkup')])

        # Call the function
        get_all_appointments()

        # Assert that execute was called with the correct query
        mock_cursor.execute.assert_called_once_with("SELECT * FROM appointments")

    @patch('crud.cursor')
    def test_get_appointment_by_id(self, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_cursor.fetchall = MagicMock(return_value=[('John', 'Doe', '12345', date(2025, 3, 15), time(10, 30), 'Checkup')])

        # Call the function
        get_appointment_by_id(1)

        # Assert that execute was called with the expected query and id
        mock_cursor.execute.assert_called_once_with(
            ("SELECT * FROM appointments WHERE id = ?", 1)
        )

    @patch('crud.cursor')
    @patch('crud.connection')
    def test_update_appointment_date(self, mock_connection, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_connection.commit = MagicMock()

        # Call the function
        update_appointment(1, date=date(2025, 3, 16))

        # Assert that execute was called with the expected query and parameters
        mock_cursor.execute.assert_called_once_with(
            ("UPDATE appointments SET date = ? WHERE id = ?", (date(2025, 3, 16), 1))
        )
        mock_connection.commit.assert_called_once()

    @patch('crud.cursor')
    @patch('crud.connection')
    def test_update_appointment_time(self, mock_connection, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_connection.commit = MagicMock()

        # Call the function
        update_appointment(1, time=time(11, 30))

        # Assert that execute was called with the expected query and parameters
        mock_cursor.execute.assert_called_once_with(
            ("UPDATE appointments SET time = ? WHERE id = ?", (time(11, 30), 1))
        )
        mock_connection.commit.assert_called_once()

    @patch('crud.cursor')
    @patch('crud.connection')
    def test_delete_appointment(self, mock_connection, mock_cursor):
        # Setup the mock
        mock_cursor.execute = MagicMock()
        mock_connection.commit = MagicMock()

        # Call the function
        delete_appointment(1)

        # Assert that execute was called with the expected query and id
        mock_cursor.execute.assert_called_once_with(
            ("DELETE FROM appointments WHERE id = ?", 1)
        )
        mock_connection.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
