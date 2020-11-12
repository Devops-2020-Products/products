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
    And I set the "Name" to "Samsung TV"
    And I press the "Search" button
    And I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Samsung TV" in the "Name" field
    And I should see "Tech" in the "Category" field
    And I should see "52 inch Samsung TV" in the "Description" field
    And I should see "3999.99" in the "Price" field
    When I press the "Clear" button
    And I set the "ID" to "2147483648"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Product with id '2147483648' was not found."

Scenario: Query Products by Price
    When I visit the "Home Page"
    And I set the "Price_Range" to "1000-4000"
    And I press the "Search" button
    Then I should see "Samsung TV" in the results
    And I should see "Samsung Galaxy 20" in the results
    And I should not see "White Bread" in the results
    And I should not see "Soap" in the results
    And I should see "52 inch Samsung TV" in the "Description" field
    And I should see "Tech" in the "Category" field
    And I should see "3999.99" in the "Price" field

Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "White Bread"
    And I press the "Search" button
    Then I should see "White Bread" in the "Name" field
    And I should see "Food" in the "Category" field
    When I change "Name" to "Wheat Bread"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see "Wheat Bread" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "Wheat Bread" in the results
    Then I should not see "White Bread" in the results
