$( function() {
        // DOM elements
    var rfp_table            = $( '.rfp_table' ),
        table_body           = rfp_table.find('tbody'),
        search_text          = $( '#search_text' ),
        search_form          = $( '#search_form' ),
        search_subscribe     = $( '#search_subscribe' ),
        search_unsubscribe     = $( '#search_unsubscribe' ),
        loader               = $( '#table_loader' ),
        logo                 = $( '#logo_main' ),
        // useful variables
        searching            = false,
        offset               = 10,
        order                = 'publish_date',
        History              = window.History,
        search_timer         = false,
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

                loader.hide();
            });
    },

    // Search ajax handler
    search_handler = function( search_keywords, order ) {
        // figure out whether to search, or just get a list of RFPs
        if ( search_keywords == '' ) {
            offset = 0;
            if ( order === undefined )
                order = 'publish_date';
            action = pagination_comet_uri;
        } else {
            action = search_comet_uri + search_keywords;
        }

        subscription_ui( false );
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

                // hide ajax loader
                loader.hide();
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
                        style: 'info',
                        text: "Undo?",
                        func: function(e) {
                            e.preventDefault();
                            subscription_handler( unsubscribe_uri, query );
                        }
                    }
                });
                // show subscribed state
            } else if ( data.status === "unsubscribed" ) {
                Alert( {
                    title: 'Done!',
                    style: 'info',
                    message: "You've unsubscribed from &ldquo;<span class='query'>"+
                        query + "</span>&rdquo;.",
                    action: {
                        text: "",
                        func: null
                    }
                });
            } else if ( data.status === 'exists' ){
                Alert( {
                    title: 'Wait.',
                    style: 'warning',
                    timeout: 4,
                    message: "You've already subscribed to &ldquo;<span class='query'>"+
                        query + "</span>&rdquo;.",
                    action: {
                        text: "Unsubscribe?",
                        func: function(e) {
                            e.preventDefault();
                            subscription_handler( unsubscribe_uri, query );
                        }
                    }
                });
            }

            // update button state at the top
            subscription_ui( data.status === 'subscribed' || 
                             data.status === 'exists' );
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
    search_form.submit( function(e) {
        e.preventDefault();
        clearInterval( search_timer );
        return search_handler( search_text.val().trim() );
    });

    logo.click( function() {
        clearInterval( search_timer );
        search_text.val( '' );
        return search_handler( '' );
    });

    // Get instant results
    search_text.keydown( function(e) {
        code = (e.keyCode ? e.keyCode : e.which);

        // show AJAX loader
        loader.show();
        // only search after 1 second after user enters a keyword
        if ( search_timer != false ) {
            clearInterval( search_timer );
            search_timer = false;
        } 

        search_timer = setTimeout( function(){
            return search_handler( search_text.val().trim() );
        }, 1000);
    });


    // Map appending of next 10 results to scroll event
    $( window ).scroll( function(e) {
        // don't paginate search results
        if ( searching ) return;

        if ( $( window ).scrollTop() == $(document).height() - $(window).height() ) {
            loader.show();
            next_page();
        }
    });
    
    // Sorting of listings behaviour
    rfp_table.find( '.title, .publish_date, .close_date' ).click( function(e){
        // don't sort searching results, for now
        if ( searching ) return;

        loader.show();
        offset = 0;
        order = $(this).attr('class');
        table_body.find('tr').remove();
        next_page();
    });
    
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

    // Dirtily detect searching
    searching = ( window.location.href.search('search') !== -1 );
});
