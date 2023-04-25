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

Scenario: List all pets
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should not see "leo" in the results

Scenario: Search for dogs
    When I visit the "Home Page"
    And I set the "Category" to "dog"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should not see "kitty" in the results
    And I should not see "leo" in the results

Scenario: Search for available
    When I visit the "Home Page"
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should see "sammy" in the results
    And I should not see "leo" in the results

Scenario: Update a Pet
    When I visit the "Home Page"
    And I set the "Name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the "Name" field
    And I should see "dog" in the "Category" field
    When I change "Name" to "Loki"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Loki" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Loki" in the results
    And I should not see "fido" in the results

## CANCEL STATUS
Scenario: Cancel order
    When I visit the "Home Page"
    Then I should see "Order Service" in the title
    And I press the "Search" button
    And I press the "Status" press button
    And I press the "Cancel" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Emilie Pourchet" in the "Name" field
    And I should see "9 Front Street" in the "Street" field
    And I should see "New York" in the "City" field
    And I should see "NY" in the "State" field
    And I should see "10543" in the "Postal Code" field
    And I should see "Canceled" in the "status"