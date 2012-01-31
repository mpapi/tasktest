## Overview ##

This is a quick first pass at executable project specifications (or bug
tracking, etc.) based on quick tests. Currently you can create a module for
your spec, write some documentation as a Python docstring, attach some metadata
using a decorator, and write some code that smoke tests a feature or bug fix
(or anticipates the feature or bug fix). The harness will execute the tests in
the module (skipping any that haven't been started yet) and generate an
overview page.


## Setup ##

    pip -E env -r dependencies.txt
    source env/bin/activate
    python spectest.py sample
    $BROWSER overview.html


## Future work ##

Lots, especially support for smoke testing web apps (request, BeautifulSoup,
lxml...).
