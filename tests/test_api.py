import pytest

def test_register_api_key(client):
    response = client.post('/auth/register', json={
        'email': 'new@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert 'api_key' in response.json

def test_get_player_profile(client, test_user):
    response = client.get(
        '/api/player/profile/magnuscarlsen',
        headers={'X-API-Key': test_user['api_key']}
    )
    assert response.status_code == 200
    assert 'stats' in response.json

def test_get_player_style(client, test_user):
    response = client.get(
        '/api/player/style/magnuscarlsen',
        headers={'X-API-Key': test_user['api_key']}
    )
    assert response.status_code == 200
    assert 'style_analysis' in response.json

def test_update_api_key(client, test_user):
    response = client.put('/auth/update', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    assert response.status_code == 200
    assert 'api_key' in response.json

def test_delete_api_key(client, test_user):
    response = client.delete('/auth/delete', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    assert response.status_code == 200