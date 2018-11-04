import logging
from . import database
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class CopyAndSaveAction(CopyToClipboardAction):

    def __init__(self, entry_id, text):
        super(CopyAndSaveAction, self).__init__(text)
        self.entry_id = entry_id

    def run(self):
        global database
        logging.info('Copy entry "%s" with the content "%s"', self.entry_id, self.text[:20])
        database.update_entry(self.entry_id)
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
