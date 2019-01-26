import os

# Using cqlsh command to import db schema
os.system('cqlsh -e "SOURCE \'schema/schema_v1.cql\'"')
