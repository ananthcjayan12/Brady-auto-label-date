import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db_path='labels.db'):
        self.db_conn = None
        if db_path == ':memory:':
            self.db_path = db_path
            self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
        else:
            self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self._init_db()

    def _get_connection(self):
        if self.db_conn:
            return self.db_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        try:
            conn = self._get_connection()
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS labels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        system_name TEXT NOT NULL,
                        year TEXT NOT NULL,
                        month TEXT NOT NULL,
                        serial_number TEXT NOT NULL,
                        printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(system_name, year, month, serial_number)
                    )
                ''')
            if not self.db_conn:
                conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def check_duplicates(self, system_name, year, month, start_serial, quantity):
        """
        Returns a list of serial numbers that are already in the database
        within the requested range.
        """
        # Determine padding from start_serial
        padding = len(start_serial)
        try:
            start_num = int(start_serial)
        except ValueError:
            return [start_serial] # Invalid input treated as duplicate for safety

        duplicates = []
        try:
            conn = self._get_connection()
            with conn:
                cursor = conn.cursor()
                for i in range(quantity):
                    current_serial = str(start_num + i).zfill(padding)
                    cursor.execute('''
                        SELECT 1 FROM labels 
                        WHERE system_name = ? AND year = ? AND month = ? AND serial_number = ?
                    ''', (system_name, year, month, current_serial))
                    if cursor.fetchone():
                        duplicates.append(current_serial)
            if not self.db_conn:
                conn.close()
        except Exception as e:
            logger.error(f"Database check error: {e}")
            raise
        
        return duplicates

    def record_prints(self, system_name, year, month, start_serial, quantity):
        """
        Records a batch of printed labels.
        """
        padding = len(start_serial)
        start_num = int(start_serial)
        
        try:
            conn = self._get_connection()
            with conn:
                cursor = conn.cursor()
                for i in range(quantity):
                    current_serial = str(start_num + i).zfill(padding)
                    cursor.execute('''
                        INSERT INTO labels (system_name, year, month, serial_number)
                        VALUES (?, ?, ?, ?)
                    ''', (system_name, year, month, current_serial))
            if not self.db_conn:
                conn.close()
        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error (duplicate serial): {e}")
            raise Exception("One or more serial numbers are already recorded.")
        except Exception as e:
            logger.error(f"Database record error: {e}")
            raise
