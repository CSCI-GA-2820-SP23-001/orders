$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_name").val(res.name);
        $("#order_street").val(res.street);
        $("#order_city").val(res.city);
        $("#order_state").val(res.state);
        $("#order_postal_code").val(res.postal_code);
        $("#order_date_created").val(res.date_created);
        $("#order_shipping_price").val(res.shipping_price);
        $("#order_status").val(res.status);
        
        // Previous code (not needed but keeping just in case)
        // if (res.available == true) {
        //     $("#pet_available").val("true");
        // } else {
        //     $("#pet_available").val("false");
        // }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#pet_name").val("");

        $("#order_id").val("");
        $("#order_name").val("");
        $("#order_street").val("");
        $("#order_city").val("");
        $("#order_state").val("");
        $("#order_postal_code").val("");
        $("#order_date_created").val("");
        $("#order_shipping_price").val("");
        $("#order_status").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#order_name").val();
        let street = $("#order_street").val();
        let city = $("#order_city").val();
        let state = $("#order_state").val();
        let postal_code = $("#order_postal_code").val();
        let date_created = $("#order_date_created").val();
        let shipping_price = $("#order_shipping_price").val();
        let status = $("#order_status").val();


        let data = {
            "name": name,
            "street": street,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "date_created": date_created,
            "shipping_price": shipping_price,
            "status": status

        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {

        let name = $("#order_name").val();
        let street = $("#order_street").val();
        let city = $("#order_city").val();
        let state = $("#order_state").val();
        let postal_code = $("#order_postal_code").val();
        let date_created = $("#order_date_created").val();
        let shipping_price = $("#order_shipping_price").val();
        let status = $("#order_status").val();

        let data = {
            "name": name,
            "street": street,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "date_created": date_created,
            "shipping_price": shipping_price,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for an ORder
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#order_name").val();
        // let street = $("#order_street").val();
        // let city = $("#order_city").val();
        // let state = $("#order_state").val();
        // let postal_code = $("#order_postal_code").val();
        // let date_created = $("#order_date_created").val();
        // let shipping_price = $("#order_shipping_price").val();
        // let status = $("#order_status").val();

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        // if (category) {
        //     if (queryString.length > 0) {
        //         queryString += '&category=' + category
        //     } else {
        //         queryString += 'category=' + category
        //     }
        // }
        // if (available) {
        //     if (queryString.length > 0) {
        //         queryString += '&available=' + available
        //     } else {
        //         queryString += 'available=' + available
        //     }
        // }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Street</th>'
            table += '<th class="col-md-2">City</th>'
            table += '<th class="col-md-2">State</th>'
            table += '<th class="col-md-2">Postal_Code</th>'
            table += '<th class="col-md-2">Date_Created</th>'
            table += '<th class="col-md-2">Shipping_Price</th>'
            table += '<th class="col-md-2">Status</th>'


            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                table +=  `<tr id="row_${i}"><td>${order.id}</td><td>${order.name}</td><td>${order.street}</td><td>${order.city}</td><td>${order.state}</td><td>${order.postal_code}</td><td>${order.shipping_price}</td><td>${order.date_created}</td><td>${order.status}</td></tr>`;
                if (i == 0) {
                    firstOrder = Order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
