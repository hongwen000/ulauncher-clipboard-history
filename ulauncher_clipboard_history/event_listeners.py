import logging
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from . import database
from .actions import CopyAndSaveAction

logger = logging.getLogger(__name__)/usr/share/albert/org.albert.extension.python/modules



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
