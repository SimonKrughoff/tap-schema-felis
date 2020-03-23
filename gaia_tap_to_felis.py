import numpy
from yaml import dump

column_dtype = numpy.dtype([('id', numpy.int),
                            ('table_name', numpy.str),
                            ('column_name', numpy.str),
                            ('datatype', numpy.str),
                            ('arraysize', numpy.str),
                            ('size', numpy.int),
                            ('description', numpy.str),
                            ('utype', numpy.str),
                            ('unit', numpy.str),
                            ('ucd', numpy.str),
                            ('principal', numpy.bool),
                            ('indexed', numpy.bool),
                            ('std', numpy.bool),
                            ('column_index', numpy.int),
                            ('table_id', numpy.int)])

table_dtype = numpy.dtype([('id', numpy.int),
                           ('schema_name', numpy.str),
                           ('table_name', numpy.str),
                           ('table_type', numpy.str),
                           ('utype', numpy.str),
                           ('description', numpy.str),
                           ('table_index', numpy.int),
                           ('schema_id', numpy.int)])

schema_dtype = numpy.dtype([('id', numpy.int),
                           ('schema_name', numpy.str),
                           ('utype', numpy.str),
                           ('description', numpy.str)])

columns_dat = numpy.genfromtxt('data/gaia_columns.csv', names=True, delimiter=':', dtype=None,
                               encoding=None)
tables_dat = numpy.genfromtxt('data/gaia_tables.csv', names=True, delimiter=':', dtype=None,
                              encoding=None)
schemas_dat = numpy.genfromtxt('data/gaia_schemas.csv', names=True, delimiter=':', dtype=None,
                               encoding=None)

schema_col_names = ['schema_name', 'description', 'utype']
table_col_names = ['schema_name', 'table_name', 'table_type', 'description', 'utype', 'table_index']
# It is supposed to have 'xtype' but gaia tables don't
#column_col_names = ['table_name', 'column_name', 'datatype', 'arraysize', 'size', 'xtype', 'description',
#                    'utype', 'unit', 'ucd', 'indexed', 'principal', 'std', 'column_index']
column_col_names = ['table_name', 'column_name', 'datatype', 'arraysize', 'size', 'description',
                    'utype', 'unit', 'ucd', 'indexed', 'principal', 'std', 'column_index']

# Check the schema has all the columns we expect
if not set(schema_col_names).issubset(set(schemas_dat.dtype.fields.keys())):
    raise ValueError('There are missing schemas columns')
if not set(table_col_names).issubset(set(tables_dat.dtype.fields.keys())):
    raise ValueError('There are missing tables columns')
if not set(column_col_names).issubset(set(columns_dat.dtype.fields.keys())):
    raise ValueError('There are missing columns columns')

schemas = {}
for r in schemas_dat:
    el = '#'+r['schema_name']
    schemas[el] = {n: r[n].item() for n in schema_col_names}
    schemas[el]['@id'] = el
    schemas[el]['tables'] = []

tables = {}
table_schema_map = {}
for r in tables_dat:
    el = '#'+'.'.join([r['schema_name'], r['table_name']])
    tables[el] = {n: r[n].item() for n in table_col_names}
    tables[el]['@id'] = el
    tables[el]['indexes'] = []
    tables[el]['columns'] = []
    tables[el]['cidx'] = []
    table_schema_map[r['table_name']] = r['schema_name'].item()

# I don't know why, but the TAP spec requires table names be unique so there is a
# one to many mapping of schema to table.  This is useful since TAP_SCHEMA also
# doesn't carry the schema name with the column descriptions.
for r in columns_dat:
    schema_name, table_name = r['table_name'].split('.')  # I'm not sure if this is spec or not
    # for some reason "catalogs" is missing from the "tables" table
    # it is in the "schemas" table
    # "gdr2_contrib" is also largely missing
    if schema_name == "catalogs" or schema_name == "gdr2_contrib":
        continue
    el = '#'+'.'.join([table_schema_map[table_name], table_name, r['column_name']])
    sel = '#'+'.'.join([table_schema_map[table_name], table_name])
    column = {n: r[n].item() for n in column_col_names}
    column['@id'] = el
    tables[sel]['columns'].append(column)
    # This will be used to sort the columns since order matters to felis
    tables[sel]['cidx'].append(r['column_index'].item())
    if r['indexed']:
        index = {'name': el+"_idx", '@id': el+"_idx", 'description': r['description'].item(), 'columns': el}
        tables[sel]['indexes'].append(index)

for t in tables:
    schemas['#'+tables[t]['schema_name']]['tables'].append(tables[t])

tap_schemas_yaml = dump(schemas, default_flow_style=False, explicit_start=True)
with open('tap_gaia.yaml', 'w') as fh:
    fh.write(tap_schemas_yaml)

# map to felis conventions
felis_schemas = {}
for s in schemas:
    felis_schemas[s] = {} 
    felis_schemas[s]['name'] = schemas[s]['schema_name']
    felis_schemas[s]['@id'] = schemas[s]['@id']
    felis_schemas[s]['description'] = schemas[s]['description']
    felis_schemas[s]['tables'] = []
    for t in schemas[s]['tables']:
        felis_schemas[s]['tables'].append({})
        felis_schemas[s]['tables'][-1]['name'] = t['table_name']
        felis_schemas[s]['tables'][-1]['@id'] = t['@id']
        felis_schemas[s]['tables'][-1]['description'] = t['description']
        felis_schemas[s]['tables'][-1]['primaryKey'] = None
        felis_schemas[s]['tables'][-1]['constraints'] = None
        felis_schemas[s]['tables'][-1]['indexes'] = t['indexes']
        columns = []
        for c in t['columns']:
            columns.append({})
            columns[-1]['name'] = c['column_name']
            columns[-1]['@id'] = c['@id']
            columns[-1]['description'] = c['description']
            columns[-1]['datatype'] = c['datatype']
            columns[-1]['value'] = None
            columns[-1]['length'] = c['size']
            columns[-1]['nullable'] = True  # This seems the safest default 
            columns[-1]['autoincrement'] = False  # This also seems safer than None e.g.
        # Columns must be in a specific order.  In felis this is the order in the description.
        # TAP OTOH supplies an index for each column.
        idx = numpy.argsort(numpy.array(t['cidx']))
        felis_schemas[s]['tables'][-1]['columns'] = [columns[i] for i in idx]

felis_schemas_yaml = dump(felis_schemas, default_flow_style=False, explicit_start=True)
with open('felis_gaia.yaml', 'w') as fh:
    fh.write(felis_schemas_yaml)
