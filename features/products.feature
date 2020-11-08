Feature: The product management service back-end
    As a Product Management Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name       | category | description | price |
        | Samsung TV       | Tech    | 52 inch Samsung TV | 3999.99|
        | Samsung Galaxy 20 | Tech    | Black Samsung phone  | 1999.99|
        | White Bread      | Food   | Wonder Bread     | 3.99|

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Soap"
    And I set the "Category" to "Toiletries"
    And I set the "Description" to "Liquid Hand Soap"
    And I set the "Price" to "1.99"
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: Read a Product
    When I visit the "Home Page"
    And I set the "ID" to "1"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Samsung TV" in the "Name" field
    And I should see "52 inch Samsung TV" in the "Description" field
    And I should see "Tech" in the "Category" field
    And I should see "3999.99" in the "Price" field
    When I press the "Clear" button
    Then the "ID" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    And the "Category" field should be empty
    And the "Price" field should be empty
    When I set the "ID" to "10"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Product with id '10' was not found."