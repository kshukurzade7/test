"""Assemble index.html from the page shell, the scene script and the shared canvas helpers."""
from pathlib import Path
here = Path(__file__).parent
helpers = (here / "helpers.js").read_text()
script = (here / "page.script.js").read_text().replace("/*HELPERS*/", helpers)
importmap = ('<script type="importmap">\n{ "imports": {\n'
             '  "three": "https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js",\n'
             '  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/"\n} }\n</script>\n')
(here / "index.html").write_text((here / "page.head.html").read_text() + importmap
                                 + '<script type="module">\n' + script + '</script>\n')
