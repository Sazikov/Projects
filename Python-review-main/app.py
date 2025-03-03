from web import app
import os
from main import parser
from config import url

if __name__ == '__main__':
    os.system("python main.py")
    app.run(port = 5000, host = "0.0.0.0", debug = True)