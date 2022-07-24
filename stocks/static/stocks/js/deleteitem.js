function deleteItem(event) {
    var companyText = $(event.target).closest("tr").text().split("\n")[1].trim();
    var endpoint = document.getElementById("deleteUrl").value;
    var csrf = $.cookie("csrftoken");
    if (endpoint) {
        $.ajax({

            url: endpoint,
            type: 'POST',
            data: {
                company: companyText,
                csrfmiddlewaretoken: csrf,
            },
            dataType: 'json',
            success: function (data) {
                console.log('done');
            },
            error: function (request, error) {
                console.log('error');
            }
        });
        event.stopPropagation();
    }
}