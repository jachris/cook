"use strict";

(function() {
    // document.getElementById('search-input').focus();

    var elems = document.querySelectorAll('h2,h3,h4,h5,h6');

    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        if (elem.id === undefined) {
            elem.id = elem.textContent
                      .toLowerCase()
                      .replace(/[ .]/g, '-')
                      .replace(/[^a-z0-9-]/g, '');
        }
        // elem.textContent = elem.textContent + ' ';
        elem.className = "jump-target";

        var a = document.createElement('a');
        a.href = '#' + elem.id;
        a.className = 'anchor-hash';
        a.appendChild(document.createTextNode('#'));
        elem.appendChild(a);
    }
})();
