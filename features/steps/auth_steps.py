from behave import given, when, then
import requests

API_URL = "http://localhost:5000"

@when('I register with email "{email}" and password "{password}"')
def register_user(context, email, password):
    context.response = requests.post(
        f"{API_URL}/auth/register",
        json={'email': email, 'password': password}
    )

@then('I should receive an API key')
def check_api_key(context):
    assert 'api_key' in context.response.json()

@given('I have registered with email "{email}" and password "{password}"')
def have_registered(context, email, password):
    context.credentials = {'email': email, 'password': password}
    context.response = requests.post(
        f"{API_URL}/auth/register",
        json=context.credentials
    )
    context.api_key = context.response.json()['api_key']

@when('I request profile for player "{username}"')
def request_profile(context, username):
    context.response = requests.get(
        f"{API_URL}/api/player/profile/{username}",
        headers={'X-API-Key': context.api_key}
    )

@then('I should receive player statistics')
def check_statistics(context):
    assert 'stats' in context.response.json()

@then('the response status code should be {status_code:d}')
def check_status_code(context, status_code):
    assert context.response.status_code == status_code
