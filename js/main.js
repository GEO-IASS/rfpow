$( function() {
    var rfp_table = $( '.rfp_table' ),
        table_body = rfp_table.find('tbody'),
        search_text = $( '#search_text' ),
        search_form = $( '#search_form' ),
        searching = false,
        offset = 10,
        order = '',
        pagination_uri = '/rfp/list/';

    // Create modal dialogue with details of each RFP
    function map_links( rfp_links ) {
        rfp_links.each( function() {
            var r = $(this);

            r.click( function(e){
                e.preventDefault();
                r.colorbox();
            });
        });
    }

    // Get next page of RFP results
    function next_page() {
        var action = pagination_uri;

        $.get( pagination_uri, { 'offset': offset, 'order' : order },

            // append HTML of RFP results received from backend
            function(data) {
                var rows = $( data );
                table_body.append( data );
                offset += rows.find( 'tr' ).length

                // map click event to modal popup handlers
                rfp_table.find('.rfp_table_link').unbind( 'click' );
                map_links( rfp_table.find('.rfp_table_link') );

                console.log( 'Grabbed next page of results. New offset: ', offset )
            });
    }


    // Initialize modal dialogues
    map_links( rfp_table.find('.rfp_table_link') );

    // Search
    search_form.submit( function(e) {
        e.preventDefault();
        var search_keywords = search_text.val().trim(),
            // no keywords? use vanilla paginated RFPList handler. 
            action = (search_keywords === '' ) ? pagination_uri 
                      : search_form.attr('action') + '/' + search_keywords;

        // now get search results via AJAX/comet
        $.get(  action,
           { 'offset': offset, 'order' : order },

            // Replace results in RFP table with what we searched for
            function(data) {
                // clean up click handlers. no need to keep trash around
                rfp_table.find('.rfp_table_link').unbind( 'click' );
                table_body.find('tr').remove();
                table_body.append( data );
                if ( search_keywords == '' ) {
                    offset = table_body.find('tr').length;
                    searching = false;
                } else {
                    searching = true;
                }

                // now re-map links to modal dialogues for search results
                map_links( table_body.find('.rfp_table_link') );
            });

        return false;
    });

    // Map appending of next 10 results to scroll to bottom event
    $( window ).scroll( function(e) {
        // don't paginate search results
        if ( searching ) return;

        if ( $( window ).scrollTop() == $(document).height() - $(window).height())
            next_page();
    })
});
