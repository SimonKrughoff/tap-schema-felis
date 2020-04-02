# Notes on converting contents of gaia's TAP_SCHEMA tables to felis
The purpose of this exploration is to get a concrete, functional experience attempting to translate tables defined according to the TAP_SCHEMA specification (specifically v1.1) to felis description files.
Internally, we are using felis as our source of primacy for all of our database holdings.
It's expected that if we are going to ingest tabular data from the community at large, it would be good to be able to consume metadata in community standard forms.
The IVOA standard for doing this is TAP_SCHEMA.
Rather than expecting the community to translate to felis, we would like to be able to take TAP_SCHEMA information and translate it to felis in as automated a process as possible.
I have taken a few notes on the process, and I have included some general issues/sharp corners I ran into along the way.
Please take note that the code provided here is not intended to be a general purpose TAP_SCHEMA to felis
converter, but is instead a first look at how difficult such a thing would be to produce.
There is no larger justification for why I used gaia as the first example other than I knew how to get the contents of the TAP_SCHEMA tables and it is a dataset I think we may want to ingest.

## Notes
* Felis docs are [here](https://felis.lsst.io/).
* TAP_SCHEMA v1.1 spec is [here](http://www.ivoa.net/documents/TAP/20170830/PR-TAP-1.1-20170830.pdf).
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
* The gaia TAP_SCHEMA does not include the `keys` and `key_columns` tables used to describe foreign key relationships.
  My reading of the TAP 1.1 spec is that all tables defined in tap schema must at least be queryable, even if empty.
  That would make the gaia TAP_SCHEMA non-compliant with the spec, though as I note below, we should be robust to missing information, if possible.
* How units are handled is not very standardized.
  Even within the entries of the gaia tap schema, there are at least two ways in which these are represented.
* The `TAP_SCHEMA` standard does not have information to indicate the primary key.
  An indication of the primary key is required in felis.
  There are heuristics I can imagind: e.g. look for an id column or assume the first one, but they don't sound very robust.
* In felis, names do not have to be unique, but `@id`s must.
* Need to be robust to TAP_SCHEMA tables having missing information.
