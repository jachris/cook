---
---

"use strict";

(function() {
    var store = [
    {% for page in site.pages %}    {
            "title": "{{ page.title | xml_escape }}",
            "content": {{
                page.content |
                strip_html |
                newline_to_br |
                replace: '<br />', ' ' |
                replace: '#', '' |
                replace: '`', '' |
                strip_newlines |
                jsonify
            }}.replace(/{:[^}]*}/g, '').replace(/ +/g, ' '),
            "url": "{{ page.url | xml_escape }}"
        }{% unless forloop.last %},{% endunless %}
    {% endfor %}
    ];

    console.log(store);

    var query = decodeURIComponent(window.location.search.substring(1));
    if (!query) {
        throw 3;
    }

    var input = document.getElementById("search-input");
    input.value = query;

    var results = [];
    var terms = query.split(" ");

    function count(str, substr) {
        var n = 0, pos = 0;

        while (true) {
            pos = str.indexOf(substr, pos);
            if (pos >= 0) {
                n++;
                pos += 1;
            } else {
                break;
            }
        }

        return n;
    }

    for (var i=0; i < store.length; i++) {
        var block = store[i];
        if (block.title === '') {
            continue;
        }

        var score = 0;

        for (var j=0; j < terms.length; j++) {
            var term = terms[j];
            score += 10 * count(block.title.toLowerCase(), term.toLowerCase());
            score += count(block.content.toLowerCase(), term.toLowerCase());
        }

        if (score > 0) {
            block.score = score;
            results.push(block);
        }
    }

    results.sort(function(a, b) {
       if (a.score < b.score) return 1;
       if (a.score > b.score) return -1;
       return 0;
    });

    console.log(results);

    var e = document.getElementById("search-results");

    if (results.length > 0) {
        for (i = 0; i < results.length; i++) {
            var result = results[i];
            var div = document.createElement('div');
            div.className = 'search-result';

            var h2 = document.createElement('h2');
            div.appendChild(h2);
            var a = document.createElement('a');
            a.href = result.url;
            h2.appendChild(a);
            var txt = document.createTextNode(result.title);
            a.appendChild(txt);

            var p = document.createElement('p');
            div.appendChild(p);
            var x = result.content.indexOf(' ', 512);
            if (x >= 0) {
                txt = document.createTextNode(result.content.substr(0, x) + '...');
            } else {
                txt = document.createTextNode(result.content + '...');
            }

            p.appendChild(txt);
            e.appendChild(div);
        }
    } else {
        e.appendChild(document.createTextNode("No results found."))
    }
})();
