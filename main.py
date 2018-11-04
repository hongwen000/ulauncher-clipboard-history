import json
import os
import logging
import os
import sqlite3
from datetime import datetime
import subprocess
import json
import html
import re
import cgi
logger = logging.getLogger(__name__)
#base_dir = os.path.dirname(__file__)

from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

class ClipboardDatabase(object):
    def __init__(self):
        pass

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
        json_arr = json.loads(output)
        items = []
        pts = term if term else "[\s\S]*"
        pattern = re.compile(pts, re.IGNORECASE)
        for json_obj in json_arr:
            row = json_obj['row']
            text = json_obj['text']
            if not text:
                text = "<i>No text</i>"
            else:
                text = pattern.sub(lambda m: "<u>%s</u>" % m.group(0), cgi.escape(" ".join(filter(None, text.replace("\n", " ").split(" ")))))
            logging.debug('Got item is: "%s" "%s"', row, text)
            items.append({
                'id': row,
                'text': text,
            })
        return items

class CopyAndSaveAction(CopyToClipboardAction):

    def __init__(self, entry_id, text):
        super(CopyAndSaveAction, self).__init__(text)
        self.entry_id = entry_id

    def run(self):
        global database
        logging.info('Copy entry "%s" with the content "%s"', self.entry_id, self.text[:20])
        #database.update_entry(self.entry_id)
        super(CopyAndSaveAction, self).run()

class ClipboardKeywordEventListener(EventListener):
    def on_event(self, event, extension):
        logging.debug('Clipboard History event: %s, argument: %s', event.__class__.__name__, event.get_argument())
        items = database.search(event.get_argument() or None)
        entries = []
        for item in items:
            entries.append(
                ExtensionResultItem(name=item['text'], on_enter=CopyAndSaveAction(item['id'], item['text']))
            )
        return RenderResultListAction(entries)

class ClipboardManagerExtension(Extension):
    def __init__(self):
        super(ClipboardManagerExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, ClipboardKeywordEventListener())

base_dir = os.path.dirname(__file__)

if __name__ == '__main__':
    manifest = json.load(open(os.path.join(base_dir, 'manifest.json'), 'rb'))
    extension_icon = manifest['icon']

    ClipboardManagerExtension().run()
