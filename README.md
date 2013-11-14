localpatches
============

Create a set of patches out of a local modifications of a third party software.

Given a standard third party (and free) software, like Invenio, detect which
files are new or modified in the local instance, and create a simple set of
patches, so they can be imported to guilt or quilt.

It may be useful to other softwares.  Or not.  But sure it has to be adapted
to them.

Quick and dirty.  Public domain.

usage: localpatches.py [-h] --upstream-dir UPSTREAM_DIR --install-dir
                       INSTALL_DIR --output-dir OUTPUT_DIR
