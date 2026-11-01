"""Use an explicit browser path or an installed Chromium; otherwise Playwright's
bundled browser. No network access is needed during test execution."""
import os
import shutil
from pathlib import Path

def chromium_path():
    specified = os.environ.get('CHROMIUM_PATH')
    if specified:
        if not Path(specified).is_file():
            raise FileNotFoundError('CHROMIUM_PATH does not point to a browser executable')
        return specified
    return shutil.which('chromium') or shutil.which('chromium-browser')
