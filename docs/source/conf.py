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

import base64
import os
import sys

import requests

module_paths = [
    os.path.abspath("../.."),
    os.path.abspath("../../slmsuite"),
    ]
for module_path in module_paths:
    sys.path.insert(0, module_path)

# -- Project information -----------------------------------------------------

project = "slmsuite"
copyright = "2022, slmsuite Developers"
author = "slmsuite Developers"
release = "0.0.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.extlinks",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "nbsphinx",
    "sphinx_copybutton",
    "sphinx_last_updated_by_git"
]

# TODO: update links on live package
extlinks = {
    "issue": ("https://github.mit.edu/cpanuski/qp-slm/issues/%s", "GH"),
    "pull": ("https://github.mit.edu/cpanuski/qp-slm/pull/%s", "PR"),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = True
autodoc_member_order = "bysource"
add_module_names = False # Remove namespaces from class/method signatures

nbsphinx_execute = "never"
nbsphinx_allow_errors = True #continue through jupyter errors

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["static"]

# Add a logo
html_theme_options = {"logo_only": True}
html_logo = "static/qp-slm.svg"

# Add a favicon
html_favicon = "static/qp-slm-notext-32x32.ico"

# https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method
def skip(app, what, name, obj, would_skip, options):
    skip_ = would_skip
    # Document `__init__`.
    if name in ("__init__",):
        skip_ = False
    # Don't document magic things.
    elif name in ("__dict__", "__doc__", "__weakref__", "__module__"):
        skip_ = True
    # Don't document private things.
    elif name[0] == '_':
        skip_ = True
    
    return skip_

examples_repo_owner = "QPG-MIT"
examples_repo_name = "slmsuite-examples"
# relative to this directory
examples_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")

def setup(app):
    app.connect("autodoc-skip-member", skip)
    app.add_css_file('css/custom.css')
    
    # Download example notebooks.
    # NOTE: GitHub API only supports downloading files up to 100 MB.
    try:
        os.makedirs(examples_path, exist_ok=True)
        tree_url = (
            "https://api.github.com/repos/{}/{}/git/trees/main?recursive=1"
            "".format(examples_repo_owner, examples_repo_name)
        )
        tree_response = requests.get(tree_url).json()
        for path_object in tree_response["tree"]:
            path_str = path_object["path"]
            if path_str[0:9] == "examples/":
                file_name = path_str[9:]
                file_path = os.path.join(examples_path, file_name)
                file_url = (
                    "https://api.github.com/repos/{}/{}/git/blobs/{}"
                    "".format(examples_repo_owner, examples_repo_name, path_object["sha"])
                )
                file_response = requests.get(file_url).json()
                file_content = file_response["content"]
                file_str = base64.b64decode(file_content.encode("utf8")).decode("utf8")
                with open(file_path, "w") as file_:
                    file_.write(file_str)
    except BaseException as e:
        print("WARNING: Unable to download example notebooks. "
              "Building without examples. Error:\n{}".format(e))

    