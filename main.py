import json
import os

from ulauncher_clipboard_history.clipboard_history import ClipboardManagerExtension

base_dir = os.path.dirname(__file__)

if __name__ == '__main__':
    manifest = json.load(open(os.path.join(base_dir, 'manifest.json'), 'rb'))
    extension_icon = manifest['icon']

    ClipboardManagerExtension().run()
