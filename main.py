import webview
import sys
import os
from api import API, resource_path, ensure_dirs

if __name__ == '__main__':
    ensure_dirs()
    html_path = resource_path('ui/index.html')

    # Ensure path format is correct for all platforms
    if sys.platform == 'win32':
        url = 'file:///' + html_path.replace('\\', '/')
    else:
        url = 'file://' + html_path

    api = API()

    window = webview.create_window(
        title='pfSense IPsec Bulk Config Generator',
        url=url,
        js_api=api,
        width=1400,
        height=900,
        min_size=(1100, 700),
        resizable=True,
        background_color='#0f1117',
    )
    webview.start(debug=False)
