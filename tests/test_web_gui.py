import webbrowser
import os
from web_gui.app import app

if not os.environ.get("WERKZEUG_RUN_MAIN"):
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    app.run(debug=True)
