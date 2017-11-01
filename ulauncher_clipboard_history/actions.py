import logging
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
