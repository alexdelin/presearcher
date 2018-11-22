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

$('.feedback-button').click(function(ev) {
    var contentJSON = $(ev.target.parentElement.parentElement.parentElement).find('.content-json')[0].innerHTML
    contentJSON = decodeURIComponent(contentJSON)
    var profileSelected = $('#profileName')[0].innerText
    // Send Feedback to API
    var data = {
        "profile_name": profileSelected,
        "feedback_type": ev.currentTarget.innerText,
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
