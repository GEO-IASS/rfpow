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
		timer  = false,
		defaults = { 
			title: "Success",
			style: "info",
			prev_style: "info",
			message: "You've subscribed",
			action: { text: "Undo", func: null }
		};

	Alert = function( o ) {
		o = $.extend( defaults, o );

		title.text( o.title );
		message.html( o.message );
		action.text( o.action.text );
		action.click( o.action.func );

		container.removeClass( o.prev_style );
		o.prev_style = o.style;
		container.addClass( o.style )
				 .fadeIn( 500 );

		clearInterval( timer );
		timer = setTimeout( function(){
			container.fadeOut(300);
		}, 1000*3 );
	};

	window.Alert = Alert;
});
