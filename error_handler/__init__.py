from flask import Flask

app = Flask(__name__)

from error_handler import handler