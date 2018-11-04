import logging
import os
import sqlite3
from datetime import datetime
import subprocess
import json
import html
import re

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

    copyq_script_getAll = r"""
    var result=[];
    for ( var i = 0; i < size(); ++i ) {
        var obj = {};
        obj.row = i;
        obj.mimetypes = str(read("?", i)).split("\n");
        obj.mimetypes.pop();
        obj.text = str(read(i));
        result.push(obj);
    }
    JSON.stringify(result);
    """

    copyq_script_getMatches = r"""
    var result=[];
    var match = "%s";
    for ( var i = 0; i < size(); ++i ) {
        if (str(read(i)).search(new RegExp(match, "i")) !== -1) {
            var obj = {};
            obj.row = i;
            obj.mimetypes = str(read("?", i)).split("\n");
            obj.mimetypes.pop();
            obj.text = str(read(i));
            result.push(obj);
        }
    }
    JSON.stringify(result);
    """

    def search(self, term=None):
        logging.debug('Search for copy entry term: "%s"', term)

        script = self.copyq_script_getMatches % term if term else self.copyq_script_getAll
        #proc = subprocess.call(['copyq', '-'], stdin=script.encode(), stdout=subprocess.PIPE)
        proc = subprocess.Popen(['copyq', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.communicate(input=script.encode())[0]
        logging.debug('Output of copyQ: "%s"', output)
        json_arr = json.loads(output)
        items = []
        pattern = re.compile(term, re.IGNORECASE)
        for json_obj in json_arr:
            row = json_obj['row']
            logging.debug('Row is: "%s"', row)
            text = json_obj['text']
            if not text:
                text = "<i>No text</i>"
            else:
                text = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), html.escape(" ".join(filter(None, text.replace("\n", " ").split(" ")))))
            items.append({
                'id': row,
                'text': text,
            })
        return items

    def update_entry(self, entry_id):
        logging.debug('Update copy entry id: "%s"', entry_id)
        query = 'UPDATE clip_entry SET timestamp = ? WHERE id = ?'
        self.cursor.execute(query, (datetime.now(), entry_id))
        self.connection.commit()

