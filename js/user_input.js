debug_ignore_validation = false

function validateNumber(field, msg, min, max) {
    if (!min) {
        min = 0
    }
    if (!max) {
        max = 255
    }
    if ((parseInt(field.value) != field.value) ||
        field.value.length < min || field.value.length > max) {
        alert(msg);
        field.focus();
        field.select();
        return false;
    }
    return true;
}

function validateString(field, msg, min, max) {
    if (field == null) {
        return true
    }


    if (!min) {
        min = 1
    }
    if (!max) {
        max = 65535
    }
    if (!field.value || field.value.length < min ||
        field.value.max > max) {
        alert(msg);
        field.focus();
        field.select();
        return false;
    }
    return true;
}

function validateEmail(email, msg) {

    var re_mail = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z])+$/;
    if (!re_mail.test(email.value)) {
        alert(msg);
        email.focus();
        email.select();
        return false;
    }

    return true;
}

function validateCCDate(date, msg) {

    var re1 = '((?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:(?:\\d{1}\\d{1})))(?![\\d])';	// MMDDYY 1
    var p = new RegExp(re1, ["i"]);
    var m = p.exec(date.value);
    if (m == null) {
        alert(msg);
        date.focus();
        date.select();
        return false;
    }

    return true;
}

/***********************************************
 * Drop Down Date select script- by JavaScriptKit.com
 * This notice MUST stay intact for use
 * Visit JavaScript Kit at http://www.javascriptkit.com/ for this script and more
 *
 * This has been modified to take into account dynamic values loaded from the server.
 ***********************************************/

var monthtext = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];

function populatedropdown(monthfield, yearfield, selectedmonth, selectedyear) {
    var today = new Date()
    var monthfield = document.getElementById(monthfield)
    var yearfield = document.getElementById(yearfield)
    var month = document.getElementById(selectedmonth)
    var year = document.getElementById(selectedyear)


    var selected_month_index = -1
    var selected_year_index = -1

    for (var m = 0; m < 12; m++) {
        monthfield.options[m] = new Option(monthtext[m], monthtext[m])
        if (month.value == monthfield.options[m].value)
            selected_month_index = m
    }

    if (selected_month_index > -1)
        monthfield.options[selected_month_index] = new Option(month.value, month.value, true, true)
    else
        monthfield.options[today.getMonth()] = new Option(monthtext[today.getMonth()], monthtext[today.getMonth()], true, true)


    var thisyear = today.getFullYear()
    for (var y = 0; y < 20; y++) {
        yearfield.options[y] = new Option(thisyear, thisyear)
        thisyear += 1
        if (year.value == yearfield.options[y].value)
            selected_year_index = y
    }

    if (selected_year_index > -1)
        yearfield.options[selected_year_index] = new Option(year.value, year.value, true, true)
    else
        yearfield.options[0] = new Option(today.getFullYear(), today.getFullYear(), true, true) //select today's year


}

$( function () {
    populatedropdown("monthdropdown", "yeardropdown", "expiry_date_month", "expiry_date_year")
});
