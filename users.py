"""
@author:
"""

import bottle

# this variable MUST be used as the name for the cookie used by this application
COOKIE_NAME = 'sessionid'

def check_login(db, usernick, password):
    """returns True if password matches stored"""



def generate_session(db, usernick):
    """create a new session and add a cookie to the request object (bottle.request)
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, use the existing sessionid in the cookie
    """



def delete_session(db, usernick):
    """remove all session table entries for this user"""



def session_user(db):
    """try to
    retrieve the user from the sessions table
    return usernick or None if no valid session is present"""


