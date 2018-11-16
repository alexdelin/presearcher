function get_content_element(title, description, score) {
    /* Logic to Draw an HTML Content element from the relevant details
    Sample:
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">
                ITEM_TITLE
            </h5>
        </div>
        <div class="row">
            <div class="card-text col-md-8">
                ITEM_DESCRIPTION
            </div>
            <div class="content-score col-md-2">
                SCORE
            </div>
            <div class="content-feedback col-md-2">
                FEEDBACK
            </div>
        </div>
    </div>
    */
    return '<div class="card"><div class="card-body"><h5 class="card-title">' + title + '</h5></div><div class="card-body row"><div class="card-text col-md-8">' + description + '</div><div class="content-score col-md-2">' + score + '</div><div class="content-feedback col-md-2">' + 'FEEDBACK' + '</div></div></div>'
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
                var contentElement = get_content_element(content['title'], content['description'], content['score'])
                $('#results-container').append(contentElement)
            });

        },
    });
});
