debug_ignore_validation = true

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

    var re1='((?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:[0-2]?\\d{1})|(?:[3][01]{1}))[-:\\/.](?:(?:\\d{1}\\d{1})))(?![\\d])';	// MMDDYY 1
    var p = new RegExp(re1,["i"]);
    var m = p.exec(date.value);
    if (m == null)
    {
        alert(msg);
        date.focus();
        date.select();
        return false;
    }

    return true;
}