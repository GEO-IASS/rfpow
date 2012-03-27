$( function() {
        // DOM elements
    var rfp_table            = $( '.rfp_table' ),
        table_body           = rfp_table.find('tbody'),
        search_text          = $( '#search_text' ),
        search_form          = $( '#search_form' ),
        search_subscribe     = $( '#search_subscribe' ),
        search_unsubscribe     = $( '#search_unsubscribe' ),
        loader               = $( '#table_loader' ),
        // useful variables
        searching            = false,
        offset               = 10,
        order                = '',
        History              = window.History,
        timer                = false,
        // URI
        pagination_comet_uri = '/rfp/list.comet',
        pagination_html_uri  = '/',
        search_comet_uri     = '/rfp/search.comet/',
        search_html_uri      = '/rfp/search/',
        subscribe_uri        = '/rfp/subscribe/',
        unsubscribe_uri      = '/rfp/unsubscribe/',

    // Create modal dialogues for each RFP's details
    map_links = function( rfp_links ) {
        rfp_links.each( function() {
            var r = $(this);

            r.click( function(e){
                e.preventDefault();
                r.colorbox();
            });
        });
    },

    // Get next chunk of RFP results. Used for infinite scroll.
    next_page = function() {
        var action = pagination_comet_uri;

        $.get( pagination_comet_uri, { 'offset': offset, 'order' : order },

            // append HTML of RFP results received from backend
            function(data) {
                var rows = $( data );
                table_body.append( data );
                offset += rows.filter('tr').length;

                // map click event to modal popup handlers
                rfp_table.find('.rfp_table_link').unbind( 'click' );
                map_links( rfp_table.find('.rfp_table_link') );

                console.log( 'Grabbed next page of results. New offset: ', offset )
            });
    },

    // Search ajax handler
    search_handler = function( search_keywords ) {
        // figure out whether to search, or just get a list of RFPs
        if ( search_keywords == '' ) {
            offset = 0;
            action = pagination_comet_uri;
        } else {
            action = search_comet_uri + search_keywords;
        }

        // now get search results via AJAX/comet
        $.get(  action, { 'offset': offset, 'order' : order },

            // Replace results in RFP table with what we searched for
            function(data) {
                // clean up click handlers. no need to keep trash around
                rfp_table.find('.rfp_table_link').unbind( 'click' );
                table_body.find('tr').remove();
                table_body.append( data );
                
                // If not searching, set offset for pagination purposes
                if ( search_keywords == '' ) {
                    offset = table_body.find('tr').length;
                    searching = false;

                    History.pushState( { search_keywords: '' }, 
                        "RFPow!", pagination_html_uri );
                // If searching, just push history state with appropriate title
                } else {
                    searching = true;
                    History.pushState( { search_keywords: search_keywords }, 
                        "RFPow! : Searching for '"+search_keywords + "'", 
                        search_html_uri + search_keywords );
                }

                // now re-map links to modal dialogues for search results
                map_links( table_body.find('.rfp_table_link') );
            });
        return false;
    },
    
    // Subscription/unsubscription handler
    subscription_handler = function( uri, query ){
        $.getJSON( uri + query, function( data ){
            if ( data.status === 'subscribed' ) {
                Alert( {
                    title: 'Hooray!',
                    message: "You've subscribed to &ldquo;<span class='query'>"+
                        query + "</span>&rdquo;.",
                    action: {
                        text: "Undo?",
                        func: function() {
                            subscription_handler( query, unsubscribe_uri );
                        }
                    }
                });
                // show subscribed state
            } else if ( data.status === "unsubscribed" ) {
                Alert( {
                    title: 'Ok!',
                    message: "You've unsubscribed from &ldquo;<span class='query'>"+
                        query + "</span>&rdquo;.",
                    action: {
                        text: "",
                        func: null
                    }
                });
            }

            // update button state at the top
            subscription_ui( data.status === 'subscribed' );
        });
    },
    // Update UI according to state of subscription
    subscription_ui = function( subscribe ) {
        if ( subscribe ) {
            search_subscribe.hide();
            search_unsubscribe.show();
        } else {
            search_subscribe.show();
            search_unsubscribe.hide();
        }
    };


    // Initialize modal dialogues
    map_links( rfp_table.find('.rfp_table_link') );

    // Map search handler to search form submission
    search_form .submit( function(e) {
        e.preventDefault();
        clearInterval( timer );
        return search_handler( search_text.val().trim() );
    });

    // Get instant results
    search_text.keydown( function(e) {
        code = (e.keyCode ? e.keyCode : e.which);

        // show AJAX loader
        loader.show();
        // only search after 1 second after user enters a keyword
        if ( timer != false ) {
            clearInterval( timer );
            timer = false;
        } 

        timer = setTimeout( function(){
            loader.hide();
            return search_handler( search_text.val().trim() );
        }, 1000);
    });


    // Map appending of next 10 results to scroll event
    $( window ).scroll( function(e) {
        // don't paginate search results
        if ( searching ) return;

        if ( $( window ).scrollTop() == $(document).height() - $(window).height() )
            next_page();
    })

    
    // History and the back button handler
    History.Adapter.bind(window, 'statechange', function(){ 
        var data = History.getState().data; 
        search_handler( data.search_keywords );
    });

    // Subscription and unsubscription event handling
    search_subscribe.click( function(e) {
        e.preventDefault();
        subscription_handler(subscribe_uri, search_text.val().trim() ) 
    });

    search_unsubscribe.click( function(e) {
        e.preventDefault();
        subscription_handler(unsubscribe_uri, search_text.val().trim()) 
    });

    // Focus on search field on load
    search_text.focus();
});
