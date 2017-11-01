import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)
base_dir = os.path.dirname(__file__)


class ClipboardDatabase(object):
    def __init__(self):
        self.connection = None
        self.cursor = None

        self.connect_db()
        self.create_table_structure()

    def connect_db(self):
        logging.debug('Connection to clipboard database...')
        db_path = os.path.join(base_dir, 'clipboard-manager.sqlite')
        self.connection = sqlite3.connect(db_path, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()
        logging.debug('Connected to clipboard database')

    def create_table_structure(self):
        logging.debug('Create table structure if not existing...')
        query = ('CREATE TABLE IF NOT EXISTS clip_entry ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                 'text TEXT, '
                 'timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')
        self.cursor.execute(query)
        self.connection.commit()

    def search(self, term=None):
        logging.debug('Search for copy entry term: "%s"', term)
        query = ("SELECT * FROM clip_entry "
                 "{where} "
                 "ORDER BY DATETIME(timestamp) DESC "
                 "LIMIT 8")
        if term:
            query = query.format(where="WHERE text LIKE ?")
            self.cursor.execute(query, ('%' + term + '%',))
        else:
            query = query.format(where='')
            self.cursor.execute(query)
        items = []
        for row in self.cursor.fetchall():
            items.append({
                'id': row[0],
                'text': row[1].encode('utf-8'),
                'timestamp': row[2],
            })

        return items

    def update_entry(self, entry_id):
        logging.debug('Update copy entry id: "%s"', entry_id)
        query = 'UPDATE clip_entry SET timestamp = ? WHERE id = ?'
        self.cursor.execute(query, (datetime.now(), entry_id))
        self.connection.commit()
