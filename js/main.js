$( function() {
    // RFP table behaviour
    var rfp_links = $('.rfp_table .rfp_table_link');

    rfp_links.each( function() {
        var r = $(this);

        r.click( function(){
            r.colorbox( {
                href: r.attr('href')
            });
        });
    });
});
