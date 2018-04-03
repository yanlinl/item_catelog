(function() {
    var header = "<header class=\"header\"><a href=\"{{url_for('categoriesPage\')}}\">Main Page</a>{%if \'username\' not in session %}<form action=\"{{url_for(\'showLogin\')}}\"><input type=\"submit\" value=\"Login\" /></form>{% else %}<form action=\"{{url_for(\'gdisconnect')}}\"><input type=\"submit\" value=\"Logout\" /></form>{% endif %}</header>";
    $(header).appendTo(document.body);
})();