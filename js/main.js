$( function() {
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

    var rfp_table = $( '.rfp_table' ),
        search_text = $( '#search_text' ),
        search_form = $( '#search_form' ),
        offset = 0,
        scroll_uri = search_form.attr('action');

    map_links( rfp_table.find('.rfp_table_link') );

    // Searching RFPs behaviour
    search_form.submit( function(e) {
        e.preventDefault();
        var table_body = rfp_table.find('tbody');

        // now get search results via AJAX/comet
        $.get( search_form.attr('action') + '/' + search_text.val(),
           // GET data
           {
                'offset': offset
           },
            // Replace results in RFP table with what we searched for
            function(data) {
                // clean up click handlers. no need to keep trash around
                rfp_table.find('.rfp_table_link').unbind( 'click' );
                table_body.find('tr').remove();
                table_body.append( data );
                offset += table_body.find('tr').length

                // now re-map links to modal dialogues for search results
                map_links( table_body.find('.rfp_table_link') );
            });

        return false;
    });
});
