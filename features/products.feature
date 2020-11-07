Feature: The pet store service back-end
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