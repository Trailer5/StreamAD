# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from os.path import dirname, abspath


sys.path.insert(0, os.path.abspath("../.."))
StreamAD_dir = dirname(dirname(dirname(abspath(__file__))))
version_path = os.path.join(StreamAD_dir, "streamad", "version.py")
exec(open(version_path).read())

# -- Project information -----------------------------------------------------

project = "StreamAD"
copyright = "2022, Fengrui-Liu"
author = "Fengrui-Liu"

# The full version, including alpha/beta/rc tags
version = __version__
release = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.bibtex",
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.ifconfig",
    # "sphinxcontrib.apidoc",
    # "myst_parser",
    "myst_nb",
    "sphinx_design",
]


source_suffix = [".rst", ".md", ".ipynb"]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]
myst_url_schemes = ("http", "https", "mailto")
myst_footnote_transition = False
nb_execution_mode = "off"
nb_execution_show_tb = "READTHEDOCS" in os.environ
html_js_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"
]
# -- nbsphinx settings -------------------------------------------------------
# nbsphinx_execute = "auto"

# Create symlinks for example notebooks
import glob

nb_files = [
    os.path.basename(f)
    for f in glob.glob(os.path.join("examples", "*.ipynb"))
    if not os.path.basename(f).startswith("temp_")
]
for nb_file in nb_files:
    target = os.path.join("../../examples", nb_file)
    if os.path.exists(target):
        os.remove(target)
    os.symlink(os.path.join("../doc/source/examples", nb_file), target)


# -- Bibliography ------------------------------------------------------------
bibtex_bibfiles = ["refs.bib"]
bibtex_default_style = "unsrtalpha"

# apidoc settings
apidoc_module_dir = "../../streamad"
apidoc_output_dir = "api"
apidoc_excluded_paths = ["**/*test*"]
apidoc_module_first = True
apidoc_separate_modules = True
apidoc_extra_args = ["-d 6"]

# mock imports
autodoc_mock_imports = [
    "pandas",
    "sklearn",
    "skimage",
    "requests",
    "cv2",
    "bs4",
    "keras",
    "seaborn",
    "PIL",
    "spacy",
    "numpy",
    "scipy",
    "matplotlib",
    "fbprophet",
    "torch",
    "transformers",
    "tqdm",
    "dill",
    "numba",
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = False

# nbsphinx_execute_arguments = [
#     "--InlineBackend.figure_formats={'svg', 'pdf'}",
#     "--InlineBackend.rc={'figure.dpi': 96}",
# ]
# nbsphinx_input_prompt = "In [%s]:"
# nbsphinx_output_prompt = "Out[%s]:"
master_doc = "index"
pygments_style = "sphinx"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["../build"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"


html_theme_options = {
    "use_repository_button": True,
    "repository_url": "https://github.com/Fengrui-Liu/StreamAD",
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


highlight_language = "none"

# Prefix document path to section labels, otherwise autogenerated labels would look like 'heading'
# rather than 'path/to/file:heading'
autosectionlabel_prefix_document = True

autodoc_default_options = {
    "members": True,
    "inherited-members": True,
}
autodoc_typehints = "none"

numpydoc_show_class_members = False
autosummary_generate = True
autosummary_imported_members = True


html_logo = "images/logo_htmlwithname.svg"
html_favicon = "images/logo_html.svg"


# -- myst-parser configuration -----------------------------------------------
# See https://myst-parser.readthedocs.io/en/stable/syntax/optional.html for
# details of available extensions.
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "smartquotes",
    "tasklist",
    "html_image",
]

# Create heading anchors for h1 to h3 (useful for local toc's)
myst_heading_anchors = 3


def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module" and name == "streamad":
        del lines[:]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)
