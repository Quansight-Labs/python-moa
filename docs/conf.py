project = 'python-moa'
copyright = '2019, Quansight'
author = 'Quansight'
version = '0.0.1'
release = '0.0.1'
extensions = [
    'sphinx.ext.mathjax',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
html_theme = 'alabaster'
html_static_path = ['_static']


def setup(app):
    app.add_js_file('mathconf.js', **{'async': 'async'})
