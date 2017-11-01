import logging
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent

from .event_listeners import ClipboardKeywordEventListener

logger = logging.getLogger(__name__)


class ClipboardManagerExtension(Extension):
    def __init__(self):
        super(ClipboardManagerExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, ClipboardKeywordEventListener())
