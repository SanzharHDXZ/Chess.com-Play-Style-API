Feature: Chess.com API Authentication
  As an API user
  I want to manage my API keys
  So that I can access the Chess.com API securely

  Scenario: Register new API key
    When I register with email "test@example.com" and password "test123"
    Then I should receive an API key
    And the response status code should be 201

  Scenario: Update API key
    Given I have registered with email "test@example.com" and password "test123"
    When I update my API key with correct credentials
    Then I should receive a new API key
    And the response status code should be 200

  Scenario: Get player profile
    Given I have a valid API key
    When I request profile for player "magnuscarlsen"
    Then I should receive player statistics
    And the response status code should be 200
