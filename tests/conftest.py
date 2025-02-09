import pytest
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY', 'test-key')
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(client):
    user_data = {
        'email': 'test@example.com',
        'password': 'test_password'
    }
    response = client.post('/auth/register', json=user_data)
    return {**user_data, 'api_key': response.json['api_key']}
