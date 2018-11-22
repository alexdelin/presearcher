function get_feedback_element() {
    return '<button type="button" class="btn btn-success \
            feedback-positive">Plus</button><button type="button" \
            class="btn btn-danger feedback-negative">Minus</button>'
};

function get_content_element(title, description, link, score, contentJSON) {
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
            <div class="content-json">' + encodeURIComponent(contentJSON) + '</div>\
            <div class="card-body">\
            <h5 class="card-title"><a href="' +
            link + '">' + title +
            '</a></h5></div><div class="card-body row">\
            <div class="card-text col-md-8">' + description +
            '</div><div class="content-score col-md-2">' + score +
            '</div><div class="content-feedback col-md-2">' +
            get_feedback_element() + '</div></div></div>'
};

function renderLastFetchedScored(last_fetched, last_scored) {
    $('#lastFetchedPlaceholder').html(last_fetched);
    $('#lastScoredPlaceholder').html(last_scored);
};

$("#fetchSubmit").click(function() {

    console.log( "Handler for fetch submit called." );

    $('#placeholder').remove()
    var profileSelected = $('#profileSelected')[0].value

    $.ajax({
        url: '/content/' + profileSelected,
        success: function(response) {

            var loadedResponse = JSON.parse(response)
            _.each(loadedResponse['content'], function(content) {
                var contentElement = get_content_element(content['title'], content['description'], content['link'], content['score'], JSON.stringify(content))
                $('#results-container').append(contentElement)
            });

            wireFeedbackButtons();
            renderLastFetchedScored(loadedResponse['last_fetched'], loadedResponse['last_scored']);

        },
    });
});

$("#reScoreSubmit").click(function() {
    console.log( "Handler for ReScore submit called." );

    $.ajax({
        type: 'POST',
        url: '/score',
        success: function() {
            alert('Re-Scored All Profiles!')
        },
    });
});

$("#subscribeSubmit").click(function() {
    console.log( "Handler for Subscribe submit called." );

    var newSubscription = $('#newSubscription')[0].value
    $.ajax({
        type: 'POST',
        url: '/subscriptions',
        data: {"url": newSubscription},
        success: function() {
            alert('Added New Subscription')
        },
    });
});

$("#createProfileSubmit").click(function() {
    console.log( "Handler for Create Profile submit called." );

    var newProfile = $('#profileName')[0].value
    $.ajax({
        type: 'POST',
        url: '/profiles',
        data: {"profile_name": newProfile},
        success: function() {
            alert('Added New Profile')
        },
    });
});

function wireFeedbackButtons() {

    $('.feedback-positive').click(function(ev) {
        var contentJSON = $(ev.target.parentElement.parentElement.parentElement).find('.content-json')[0].innerHTML
        contentJSON = decodeURIComponent(contentJSON)
        var profileSelected = $('#profileName')[0].innerText
        // Send Feedback to API
        var data = {
            "profile_name": profileSelected,
            "feedback_type": "pos",
            "content": contentJSON
        }
        $.ajax({
            type: 'POST',
            url: '/feedback',
            data: JSON.stringify(data),
            success: function() {
                alert('Added Feedback!')
            }
        });
    });

    $('.feedback-negative').click(function(ev) {
        var contentJSON = $(ev.target.parentElement.parentElement.parentElement).find('.content-json')[0].innerHTML
        contentJSON = decodeURIComponent(contentJSON)
        var profileSelected = $('#profileName')[0].innerText
        // Send Feedback to API
        var data = {
            "profile_name": profileSelected,
            "feedback_type": "neg",
            "content": contentJSON
        }
        $.ajax({
            type: 'POST',
            url: '/feedback',
            data: JSON.stringify(data),
            success: function() {
                alert('Added Feedback!')
            }
        });
    })
};

wireFeedbackButtons();
