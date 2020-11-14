$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_category").val(res.category);
        $("#product_description").val(res.description);
        $("#product_price").val(res.price);
        $("#product_price_range").val("");
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#product_name").val("");
        $("#product_category").val("");
        $("#product_description").val("");
        $("#product_price").val("");
        $("#product_price_range").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#product_name").val();
        var description = $("#product_description").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();

        var data = {
            "name": name,
            "description": description,
            "category": category,
            "price": price
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/products",
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
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();
        var name = $("#product_name").val();
        var description = $("#product_description").val();
        var category = $("#product_category").val();
        var price = $("#product_price").val();

        var data = {
            "name": name,
            "description": description,
            "category": category,
            "price": price
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/products/" + product_id,
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
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/products/" + product_id,
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
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/products/" + product_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Purchase a Product
    // ****************************************

    $("#purchase-btn").click(function () {

        var product_id = $("#product_id").val();
        var product_amount = $("#product_amount").val();
        
        var data = {
            "amount": product_amount,
            "shopcart_id": None
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/products/" + product_id + "/purchase",
            contentType: "application/json",
            data: JSON.stringify(data),
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been purchased!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#product_name").val();
        var description = $("#product_description").val();
        var category = $("#product_category").val();
        var price_range = $("#product_price_range").val();
        var flag = 0;

        var queryString = "";

        if (name) {
            queryString += 'name=' + name
        }
        else if (category) {
            queryString += 'category=' + category
        }
        else if (description) {
            queryString += 'description=' + description
        }
        else if (price_range) {
            var prices = price_range.split('-');
            var price_min = prices[0];
            var price_max = prices[1];
            queryString += 'minimum=' + price_min;
            queryString += '&maximum=' + price_max;
            flag = 1
        }

        if (flag===0) {

            var ajax = $.ajax({
                type: "GET",
                url: "/products?" + queryString,
                contentType: "application/json",
                data: ''
            })
        }
        else{
            var ajax = $.ajax({
                type: "GET",
                url: "/products/price?" + queryString,
                contentType: "application/json",
                data: ''
            })
            flag = 0
        }

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:40%">Name</th>'
            header += '<th style="width:40%">Description</th>'
            header += '<th style="width:40%">Category</th>'
            header += '<th style="width:10%">Price</th></tr>'
            $("#search_results").append(header);
            var firstProduct = "";
            for(var i = 0; i < res.length; i++) {
                var product = res[i];
                var row = "<tr><td>"+product.id+"</td><td>"+product.name+"</td><td>"+product.description+"</td><td>"+product.category+"</td><td>"+product.price+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstProduct = product;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstProduct != "") {
                update_form_data(firstProduct)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
