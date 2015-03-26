"""
@author: Steve Cassidy
"""

import unittest

from database import COMP249Db
from http.cookies import SimpleCookie

# import the modules to be tested
import users, interface
from bottle import request, response


class Test(unittest.TestCase):

    def setUp(self):
        # open an in-memory database for testing
        self.db = COMP249Db(':memory:')
        self.db.create_tables()
        self.db.sample_data(random=False)
        self.users = self.db.users
        self.posts = self.db.posts

    def test_check_login(self):

        for password, nick, avatar in self.users:
            # try the correct password
            self.assertTrue(users.check_login(self.db, nick, password), "Password check failed for nick %s" % nick)

            # and now incorrect
            self.assertFalse(users.check_login(self.db, nick, "badpassword"), "Bad Password check failed for nick %s" % nick)

        # check for an unknown email
        self.assertFalse(users.check_login(self.db, "unknownperson", "badpassword"), "Bad Password check failed for unknown user")

    def get_cookie_value(self, cookiename):
        """Get the value of a cookie from the bottle response headers"""

        headers = response.headerlist
        for h,v in headers:
            if h == 'Set-Cookie':
                cookie = SimpleCookie(v)
                if cookiename in cookie:
                    return cookie[cookiename].value

        return None

    def test_generate_session(self):
        """The generate_session procedure makes a new session cookie
        to be returned to the client
        If there is already a session active for this user, return the
        same session key in the cookie"""

        # run tests for all test users
        for password, nick, avatar in self.users:

            users.generate_session(self.db, nick)
            # get the sessionid from the response cookie

            sessionid = self.get_cookie_value(users.COOKIE_NAME)

            self.assertFalse(sessionid is None)

            cursor = self.db.cursor()
            cursor.execute('select usernick from sessions where sessionid=?', (sessionid,))

            query_result = cursor.fetchone()
            if query_result is None:
                self.fail("No entry for session id %s in sessions table" % (sessionid,))

            self.assertEqual(nick, query_result[0])

            # now try to make a new session for one of the users

            users.generate_session(self.db, nick)

            sessionid2 = self.get_cookie_value(users.COOKIE_NAME)

            # sessionid should be the same as before

            self.assertEqual(sessionid, sessionid2)

        # try to generate a session for an invalid user

        sessionid3 = users.generate_session(self.db, "Unknown")
        self.assertEqual(sessionid3, None, "Invalid user should return None from generate_session")


    def test_delete_session(self):
        """The delete_session procedure should remove all sessions for
        a given user in the sessions table.
        Test relies on working generate_session"""

        # run tests for all test users
        for passwd, nick, avatar in self.users:
            users.generate_session(self.db, nick)

            # now remove the session
            users.delete_session(self.db, nick)

            # now check that the session is not present

            cursor = self.db.cursor()
            cursor.execute('select sessionid from sessions where usernick=?', (nick,))

            rows = cursor.fetchall()
            self.assertEqual(rows, [], "Expected no results for sessions query from deleted session, got %s" % (rows,))


    def test_session_user(self):
        """The session_user procedure finds the name of the logged in
        user from the session cookie if present

        Test relies on working generate_session
        """

        # first test with no cookie
        nick_from_cookie = users.session_user(self.db)
        self.assertEqual(nick_from_cookie, None, "Expected None in case with no cookie, got %s" % str(nick_from_cookie))

        request.cookies[users.COOKIE_NAME] = 'fake sessionid'
        nick_from_cookie = users.session_user(self.db)

        self.assertEqual(nick_from_cookie, None, "Expected None in case with invalid session id, got %s" % str(nick_from_cookie))

        # run tests for all test users
        for password, nick, avatar in self.users:

            users.generate_session(self.db, nick)

            sessionid = self.get_cookie_value(users.COOKIE_NAME)

            request.cookies[users.COOKIE_NAME] = sessionid

            nick_from_cookie = users.session_user(self.db)

            self.assertEqual(nick_from_cookie, nick)


    def test_post_add(self):
        """Test adding new posts"""

        usernick = 'Bean'
        message = "one two three"

        postid = interface.post_add(self.db, usernick, message)

        # result should be an integer
        self.assertEqual(int, type(postid))

        # get all posts for this user (should be just one)
        posts = interface.post_list(self.db, usernick=usernick)
        self.assertEquals(1, len(posts))

        # check it's the same
        self.assertEquals(postid, posts[0][0])


    def test_post_add_length(self):
        """Posting a long message should fail"""

        usernick = 'Bean'
        longmessage = "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789"
        result = interface.post_add(self.db, usernick, longmessage)

        self.assertEqual(None, result)



if __name__ == "__main__":
    unittest.main()