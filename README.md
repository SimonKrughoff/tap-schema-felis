# Notes on converting contents of gaia's TAP_SCHEMA tables to felis

Felis docs are [here](https://felis.lsst.io/).
TAP_SCHEMA v1.1 spec is [here](http://www.ivoa.net/documents/TAP/20170830/PR-TAP-1.1-20170830.pdf).

## Notes
* I downloaded the table contents in CSV format from [here](https://gaia.aip.de/query/).
  * `select * from TAP_SCHEMA.schemas`
  * `select * from TAP_SCHEMA.tables`
  * `select * from TAP_SCHEMA.columns`
* It turns out some descriptions in the tables and columns files had commas in their descriptions which breaks `numpy.genfromtxt` so I converted them to `:` delimited by hand.
* To produce the yaml descriptions, execute the conversion script `python gaia_tap_to_felis.pygaia_tap_to_felis.py`
  The script has the locations to the TAP_SCHEMA files hard coded.
  Note that there are two files:
    * tap_gaia.yaml: is simply a yaml serialization of a dictionary of attributes constructed from the input TAP_SCHEMA tables.
    * felis_gaia.yaml: is the felis description and is intended to be as compliant as possible without human intervention.

## General issues
* How units are handled is not very standardized.
  Even within the entries of the gaia tap schema, there are at least two ways in which these are represented.
* The `TAP_SCHEMA` standard does not have information to indicate the primary key.
  An indication of the primary key is required in felis.
  There are heuristics I can imagind: e.g. look for an id column or assume the first one, but they don't sound very robust.
* In felis, names do not have to be unique, but `@id`s must.
* Need to be robust to TAP_SCHEMA tables having missing information.
