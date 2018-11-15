function get_content_element(title, description, rating) {
    /* Logic to Draw an HTML Content element from the relevant details
    Sample:
    <div class="content-recommendation row">
        <div class="content-title col-md-12">
            ITEM_TITLE
        </div>
    </div>
    <div class="row">
        <div class="content-description col-md-8">
            ITEM_DESCRIPTION
        </div>
        <div class="content-rating col-md-2">
            RATING
        </div>
        <div class="content-feedback col-md-2">
            FEEDBACK
        </div>
    </div>
    */
    return '<div class="content-recommendation row"><div class="content-title col-md-12">' + title + '</div></div><div class="row"><div class="content-description col-md-8">' + description + '</div><div class="content-rating col-md-2">' + rating + '</div><div class="content-feedback col-md-2">' + 'FEEDBACK' + '</div></div>'
}

$("#fetchSubmit").click(function() {

    console.log( "Handler for fetch submit called." );

    $('#placeholder').remove()
    var profileSelected = $('#profileSelected')[0].value

    $.ajax({
        url: '/content/' + profileSelected,
        success: function(response) {

            var loadedResponse = JSON.parse(response)
            _.each(loadedResponse, function(content) {
                // var contentElement = '<tr class="content-recommendation"><td>' + content['title'] + '</td></tr>'
                var contentElement = get_content_element(content['title'], content['description'], 0.9)
                $('#results-container').append(contentElement)
            });

        },
    });
});
