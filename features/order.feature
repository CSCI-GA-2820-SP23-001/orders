Feature: The order store service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keep track of all the orders

Background:
    Given the following orders
        | name             | street              | city           | state   | postal code   |
        | Emilie Pourchet  | 9 Front Street      | New York       | NY      | 10543         |
        | Jane Doe         | 140 E 7th Street    | Philadelphia   | PA      | 10009         |
        | John Doe         | 55 Danner Court     | Atlanta        | GA      | 29089         |
        | Random Name      | 20 Harrison Avenue  | Memphis        | TN      | 30909         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Name" to "Emilie Pourchet"
    And I set the "Street" to "9 Front Street"
    And I set the "City" to "New York"
    And I set the "State" to "NY"
    And I set the "Postal Code" to "10543"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Street" field should be empty
    And the "City" field should be empty
    And the "State" field should be empty
    And the "Postal Code" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Emilie Pourchet" in the "Name" field
    And I should see "9 Front Street" in the "Street" field
    And I should see "New York" in the "City" field
    And I should see "NY" in the "State" field
    And I should see "10543" in the "Postal Code" field

Scenario: List all orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Emilie Pourchet" in the results
    And I should see "Jane Doe" in the results
    And I should not see "John Doe" in the results


Scenario: Query for city
    When I visit the "Home Page"
    And I set the "city" to "new york"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Emilie Pourchet" in the results
    And I should not see "Jane Doe" in the results
    And I should not see "John Doe" in the results


Scenario: Delete an Order
    When I visit the "Home Page"
    And I set the "Name" to "Emilie Pourchet"
    And I set the "Street" to "9 Front Street"
    And I set the "City" to "New York"
    And I set the "State" to "NY"
    And I set the "Postal Code" to "10543"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Street" field should be empty
    And the "City" field should be empty
    And the "State" field should be empty
    And the "Postal Code" field should be empty
    When I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    Then the "Id" field should be empty
    And the "Name" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "NOT FOUND"

Scenario: Read and Update an Order
    When I visit the "Home Page"
    And I set the "Name" to "Jane Doe"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jane Doe" in the "Name" field
    And I should see "140 E 7th Street" in the "street" field
    When I change "Name" to "Victoria Obasa"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Victoria Obasa" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Victoria Obasa" in the results
    And I should not see "Jane Doe" in the results
