"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test_2"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """test model for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        user_1 = User.signup("user1",'user1@gmail.com','password', None)
        user_2 = User.signup("user2",'user2@gmail.com','password', None)
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()
        self.user_1 = user_1
        self.user_1_id = user_1.id
        self.user_2 = user_2
        self.user_2_id = user_2.id

        self.client = app.test_client()

    def tearDown(self):
        '''Clean up test db or any bad transaction '''
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        ''' Test representation of user'''
        
        u1_repr = f"<User #{self.user_1.id}: {self.user_1.username}, {self.user_1.email}>"
        u2_repr = f"<User #{self.user_2.id}: {self.user_2.username}, {self.user_2.email}>"
        self.assertEqual(self.user_1.__repr__(), u1_repr)
        self.assertEqual(self.user_2.__repr__(), u2_repr)
    
    def test_follows(self):
        self.user_1.following.append(self.user_2)
        db.session.commit()
        self.assertEqual(len(self.user_2.followers),1)
        self.assertEqual(len(self.user_1.following),1)

        self.assertEqual(len(self.user_2.following),0)
        self.assertEqual(len(self.user_1.followers),0)

    def test_is_followed_by(self):
        '''Is this user followed by other user, test case'''
        self.assertFalse(self.user_2.is_followed_by(self.user_1))
        self.user_1.following.append(self.user_2)
        db.session.commit()
        self.assertTrue(self.user_2.is_followed_by(self.user_1))
    
    def test_is_following(self):
        '''is this user folling other user, test case'''
        self.assertFalse(self.user_1.is_following(self.user_2))
        self.user_1.following.append(self.user_2)
        db.session.commit()
        self.assertTrue(self.user_1.is_following(self.user_2))
    

    def test_user_signup(self):
        '''testing signup/create functionality'''
        valid_user = User.signup("valid_user",'valid@gmail.com','password', None)
        db.session.add(valid_user)
        db.session.commit()
        user = User.query.get(valid_user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, valid_user.username)
        self.assertEqual(user.email, valid_user.email)
    
    def test_invalid_user_signup(self):
        invalid_user = User.signup("user1",'user1@gmail.com','password', None)
        #these are user1's credentials
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()
    
    def test_user_authenticate_success(self):
        user = User.authenticate(self.user_1.username, 'password')
        self.assertEqual(user.id, self.user_1.id)
    
    def test_user_authenticate_fail(self):
        user = User.authenticate(self.user_1.username,'notapassword')
        user_2 = User.authenticate('notauser','password')
        self.assertFalse(user)
        self.assertFalse(user_2)