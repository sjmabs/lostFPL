from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a0269ebf979cace96d9659222c7102b0'

from flaskFPL import routes

