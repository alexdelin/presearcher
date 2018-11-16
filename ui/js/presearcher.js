function get_feedback_element() {
    return '<button type="button" class="btn btn-success \
            feedback-positive">Plus</button><button type="button" \
            class="btn btn-danger feedback-negative">Minus</button>'
}

function get_content_element(title, description, link, score) {
    /* Logic to Draw an HTML Content element from the relevant details
    Sample:
    <div class="card content-recommendation">
        <div class="card-body">
            <h5 class="card-title">
                <a href="ITEM_LINK">
                    ITEM_TITLE
                </a>
            </h5>
        </div>
        <div class="card-body row">
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

    return '<div class="card content-recommendation">\
            <div class="card-body">\
            <h5 class="card-title"><a href="' +
            link + '">' + title +
            '</a></h5></div><div class="card-body row">\
            <div class="card-text col-md-8">' + description +
            '</div><div class="content-score col-md-2">' + score +
            '</div><div class="content-feedback col-md-2">' +
            get_feedback_element() + '</div></div></div>'
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
                var contentElement = get_content_element(content['title'], content['description'], content['link'], content['score'])
                $('#results-container').append(contentElement)
            });

        },
    });
});
