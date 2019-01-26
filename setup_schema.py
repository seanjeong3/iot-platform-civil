import os

# Using cqlsh command to import db schema
print("Start importing Cassandra database schema from schema/schema_v1.cql")
os.system('cqlsh -e "SOURCE \'schema/schema_v1.cql\'"')
print("Data schema has been successfully imported")