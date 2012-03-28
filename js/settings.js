/*
 * UI javascript for the account settings page.
 */

$( function() {
	// Unsubscription behaviour
	$( '.unsubscribe' ).click( function(e){
		var that            = $( this ),
			container       = that.parent('.subscription'),
			keyword         = that.attr( 'data-keyword' ),
			unsubscribe_uri = '/rfp/unsubscribe/';

		$.getJSON( unsubscribe_uri + keyword, function( data ) {
			if ( data.status !== "unsubscribed" ) return;

			// notify user all went well
			Alert( {
				title: 'Super!',
				style: 'info',
				message: "You've unsubscribed from &ldquo;<span class='query'>"+
					keyword + "</span>&rdquo;.",
				action: {
					text: "",
					func: null
				}
			});

			// remove keyword div from table
			container.fadeOut(500);

		});
	});

});
