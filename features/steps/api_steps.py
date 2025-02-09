from behave import given, when, then
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

API_URL = "http://localhost:5000"

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

def wait_for_api():
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = http.get(f"{API_URL}/api/docs")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            if attempt < max_attempts - 1:
                time.sleep(2)  # Wait 2 seconds before retrying
            continue
    return False

@when('I register with email "{email}" and password "{password}"')
def register_user(context, email, password):
    if not wait_for_api():
        raise Exception("API is not available after multiple attempts")
    
    try:
        context.response = http.post(
            f"{API_URL}/auth/register",
            json={'email': email, 'password': password},
            timeout=10
        )
        context.email = email  # Store email for later use
        context.password = password  # Store password for later use
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to register: {str(e)}")

@when('I update my API key with email "{email}" and password "{password}"')
def update_api_key(context, email, password):
    if not wait_for_api():
        raise Exception("API is not available after multiple attempts")
    
    try:
        context.response = http.put(
            f"{API_URL}/auth/update",
            json={'email': email, 'password': password},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to update API key: {str(e)}")

@when('I delete my API key with email "{email}" and password "{password}"')
def delete_api_key(context, email, password):
    if not wait_for_api():
        raise Exception("API is not available after multiple attempts")
    
    try:
        context.response = http.delete(
            f"{API_URL}/auth/delete",
            json={'email': email, 'password': password},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to delete API key: {str(e)}")

@when('I request profile for player "{username}"')
def request_profile(context, username):
    if not wait_for_api():
        raise Exception("API is not available after multiple attempts")
    
    if not hasattr(context, 'email') or not hasattr(context, 'password'):
        raise Exception("User not registered. Please register first.")
    
    # Register the user if not already registered
    if not hasattr(context, 'api_key'):
        register_user(context, context.email, context.password)
        if context.response.status_code != 201:
            raise Exception(f"Failed to register user: {context.response.text}")
        context.api_key = context.response.json()['api_key']
    
    try:
        context.response = http.get(
            f"{API_URL}/api/player/profile/{username}",
            headers={'X-API-Key': context.api_key},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get player profile: {str(e)}")

@when('I request style analysis for player "{username}"')
def request_style_analysis(context, username):
    if not wait_for_api():
        raise Exception("API is not available after multiple attempts")
    
    if not hasattr(context, 'email') or not hasattr(context, 'password'):
        raise Exception("User not registered. Please register first.")
    
    # Register the user if not already registered
    if not hasattr(context, 'api_key'):
        register_user(context, context.email, context.password)
        if context.response.status_code != 201:
            raise Exception(f"Failed to register user: {context.response.text}")
        context.api_key = context.response.json()['api_key']
    
    try:
        context.response = http.get(
            f"{API_URL}/api/player/style/{username}",
            headers={'X-API-Key': context.api_key},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get player style analysis: {str(e)}")

@given('I have registered with email "{email}" and password "{password}"')
def have_registered(context, email, password):
    if not wait_for_api():
        raise Exception("API is not available after multiple attempts")
    
    try:
        context.email = email
        context.password = password
        context.credentials = {'email': email, 'password': password}
        context.response = http.post(
            f"{API_URL}/auth/register",
            json=context.credentials,
            timeout=10
        )
        if context.response.status_code == 201:
            context.api_key = context.response.json()['api_key']
        else:
            raise Exception(f"Registration failed with status code: {context.response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to register: {str(e)}")

@then('the response status code should be {status_code:d}')
def check_status_code(context, status_code):
    assert hasattr(context, 'response'), "No response received"
    assert context.response.status_code == status_code, \
        f"Expected status code {status_code}, got {context.response.status_code}. Response: {context.response.text}"

@then('the response should contain an API key')
def check_api_key(context):
    assert hasattr(context, 'response'), "No response received"
    assert 'api_key' in context.response.json(), "No API key in response"
    assert len(context.response.json()['api_key']) > 0, "Empty API key received"

@then('the response should contain player stats')
def check_player_stats(context):
    assert hasattr(context, 'response'), "No response received"
    assert 'stats' in context.response.json(), "No player stats in response"

@then('the response should contain style analysis')
def check_style_analysis(context):
    assert hasattr(context, 'response'), "No response received"
    assert 'style_analysis' in context.response.json(), "No style analysis in response"
