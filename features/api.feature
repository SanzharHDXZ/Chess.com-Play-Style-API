Feature: Chess.com API Endpoints
  As an API user
  I want to test the API endpoints
  So that I can ensure they are working correctly

  Scenario: Register a new API key
    When I register with email "new@example.com" and password "password123"
    Then the response status code should be 201
    And the response should contain an API key

  Scenario: Update an existing API key
    Given I have registered with email "update@example.com" and password "old_password"
    When I update my API key with email "update@example.com" and password "old_password"
    Then the response status code should be 200
    And the response should contain an API key

  Scenario: Delete an existing API key
    Given I have registered with email "delete@example.com" and password "delete_password"
    When I delete my API key with email "delete@example.com" and password "delete_password"
    Then the response status code should be 200

  Scenario: Get player profile
    Given I have registered with email "profile@example.com" and password "profile_password"
    When I request profile for player "magnuscarlsen"
    Then the response status code should be 200
    And the response should contain player stats

  Scenario: Get player style
    Given I have registered with email "style@example.com" and password "style_password"
    When I request style analysis for player "magnuscarlsen"
    Then the response status code should be 200
    And the response should contain style analysis
