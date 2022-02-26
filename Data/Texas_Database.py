from faker import Faker
from faker_vehicle import VehicleProvider
import pandas as pd
from faker.providers import automotive
import random

def licence_plate():
    from random import choice
    import string
    import random
    letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    number = ''.join([choice(letter) for i in range(3)] + [" "] +[choice(string.digits) for i in range(3)])
    return number

def vin_number():
    from random import choice
    import string
    import random
    letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    number = ''.join([choice(string.digits) for i in range(1)] + 
                [""] +[choice(letter) for i in range(4)] + 
                [""] +[choice(string.digits) for i in range(2)] +
                [""] +[choice(letter) for i in range(4)] +
                [""] +[choice(string.digits) for i in range(6)]     
                )
    return number

fake = Faker("en_US")

fake.add_provider(VehicleProvider)

license_plate_list_status = ["Pending", "Permanent","Temporary", "Not in Database"]

ident = {}
for i in range(0,100000):
    ident[i] = {}    
    ident[i]["First Name"] = fake.first_name()
    ident[i]["First Name"] = fake.first_name()
    ident[i]["Last Name"] = fake.last_name()
    ident[i]["Social Security"] = fake.ssn() # not included in smart contract
    ident[i]["License Plate"] = licence_plate()
    ident[i]["VIN Number"] = vin_number()
    ident[i]["License Plate Status"] = random.choice(license_plate_list_status)
    ident[i]["Address 1"] = fake.street_address()
    ident[i]["City"] = fake.city()
    ident[i]["Postal Code"] = fake.zipcode_in_state("TX")
    ident[i]["State"] = "Texas"
    ident[i]["Country"] = fake.current_country()
    ident[i]["Vehicle"] = fake.vehicle_object()


v_list = []
for i in range(0,100000):
    v_list.append(ident[i]["Vehicle"])

df_info = pd.DataFrame(ident).transpose().drop(columns="Vehicle")
df_vehicle = pd.DataFrame(v_list)

df = pd.merge(
    left=df_info,
    right = df_vehicle,
    how = "outer",
    on = df_info.index
).drop("key_0",axis=1)

import sqlalchemy

connection_string = "sqlite:///database_file.db"

engine = sqlalchemy.create_engine(connection_string)

df.to_sql(
    name="Texas License Plates",
    con=engine,
    if_exists="replace",
    index=True)

engine.table_names() 

print(pd.read_sql_table("Texas License Plates", con=engine).T) 