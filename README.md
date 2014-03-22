Campfire Export
===============

This script exports all campfire transcripts to a database using Pinder and
SqlAlchemy. This script will also keep a database managed by the script up to
date by simply rerunning the script.

Installation
------------

  1. In a virtual environment run `python setup.py install` to install any
     dependencies.
  2. Modify the sample.cfg file to add your subdomain and user token. Also if
     you would like to change the database url do that as well.
  3. Run `python sync.py <path to configuration file>` to start the process of
     downloading all campfire transcripts
