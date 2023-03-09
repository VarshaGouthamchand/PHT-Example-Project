import os
import pandas as pd
import json
import subprocess
import pathlib
import shutil

# read database uri
database_uri = os.getenv('DATABASE_URI','no_database_uri')

# read/query data from database_uri
#database_uri = "/mnt/c/Users/P70070487/Downloads/pht_example_train-master/pht_example_train-master/Dataset/Houston.csv"
#database_uri = "Dataset/Houston.csv"
#data = pd.read_csv(database_uri)

shutil.copy2(database_uri, os.path.dirname(database_uri) +'/database.csv')

try:
	f = open("triplifierCSV.properties", "w")
	f.write("jdbc.url = jdbc:relique:csv:" + str(os.path.dirname(database_uri)) + "?fileExtension=.csv\njdbc.user = \njdbc.password = \njdbc.driver = org.relique.jdbc.csv.CsvDriver\n\n"
		"repo.type = rdf4j\nrepo.url = http://host.docker.internal:7200\nrepo.id = userRepo")
	f.close()
	args1 = "java -jar /app/javaTool/triplifier.jar -p triplifierCSV.properties"
	command_run = subprocess.call(args1, shell=True)
except Exception as err:
	print(err)
	message = "Triplifier run Unsucessful"
	#flash(err)
if command_run == 0:
	message = "Triplifier run successful!"
else:
	message = "Triplifier run Unsuccessful!"

if os.path.exists(os.path.dirname(database_uri) +'/database.csv'):
	os.remove(os.path.dirname(database_uri) +'/database.csv')

with open('output.txt', 'w') as f:
	f.write(message)
	