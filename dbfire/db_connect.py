"""
© 2019 Rouge Media All Rights Reserved.

Connection to Firebase Realtime Storage

"""

import firebase_admin
from firebase_admin import credentials, db
import os
# TODO: Better ways to secure credentials. Environment Vars or Secret Manager
CERT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         'authentication_files/rogue-media-project-firebase-adminsdk-kv4p4-42f48789b9.json')
DB_URL = 'https://rogue-media-project-default-rtdb.firebaseio.com/'
fire_cred = credentials.Certificate(CERT_FILE)
fire_app = firebase_admin.initialize_app(fire_cred, {'databaseURL': DB_URL})


def get_db_ref(path='/'):
    """
    Fetch database reference of path provided
    :param path: Path of Database Object
    :returns DB reference
    """
    return db.reference(path)
