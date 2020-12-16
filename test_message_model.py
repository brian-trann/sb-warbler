"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
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


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        user_1 = User.signup("user1",'user1@gmail.com','password', None)
        
        db.session.add(user_1)
        db.session.commit()
        self.user_1 = user_1
    
        self.client = app.test_client()

    def tearDown(self):
        '''Clean up test db or any bad transaction '''
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        self.assertEqual(len(self.user_1.messages), 0)
        msg = Message(text="thisisatest",user_id=self.user_1.id)
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user_1.messages), 1)
        

    def test_message_like(self):
        msg_1 = Message(text="thisisatest",user_id=self.user_1.id)
        msg_2 = Message(text="second",user_id=self.user_1.id)
        user_2 = User.signup("user2",'user2@gmail.com','password', None)
        db.session.add_all([msg_1,msg_2,user_2])
        db.session.commit()
        like_count_before = Likes.query.filter(Likes.user_id == user_2.id).count()
        self.assertEqual(like_count_before,0)
        user_2.likes.append(msg_2)
        db.session.commit()
        like_count_after = Likes.query.filter(Likes.user_id == user_2.id).count()
        self.assertEqual(like_count_after,1)

        
        