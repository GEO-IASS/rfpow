// 
// Class for making pretty alerts
//
// Parameters:
//  title -- title of message
//  message -- body of the message. Don't make too long.
//  link -- follow-up actions in the alert, e.g. "undo"
//

$(function(){
	var container = $( '#alert_container' ),
		title = container.find( '.title' ),
		message = container.find( '.message' ),
		action = container.find( '.action' ),
		defaults = { 
			title: "Success",
			message: "You've subscribed",
			action: { text: "Undo", func: null }
		};

	Alert = function( o ) {
		o = $.extend( defaults, o );

		title.text( o.title );
		message.text( o.message );
		action.text( o.action.text );
		action.click( o.action.func );

		container.fadeIn( 500 );

		var timer = setTimeout( function(){
			container.fadeOut(300);
		}, 1000*3 );
	};

	window.Alert = Alert;
});
