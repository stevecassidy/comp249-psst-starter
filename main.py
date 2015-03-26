__author__ = 'Steve Cassidy'

from bottle import Bottle, template, static_file, request, response, HTTPError
import interface
import users
from database import COMP249Db


application = Bottle()

@application.route('/')
def index():

    db = COMP249Db()

    return template('general', title="Psst!", content="Get Started")



@application.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')




if __name__ == '__main__':
    application.run(debug=True)