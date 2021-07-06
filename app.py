#import flask dependency
from flask import Flask

#create new flask app
app = Flask(__name__)

#create flask routes
#define starting point
@app.route('/')
def hello_world():
    return 'Hello World'
