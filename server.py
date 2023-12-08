import json
import re
import socket

import pymongo

ip_address = "127.0.0.1"
port = 9999
bufferSize = 1024
client = pymongo.MongoClient("mongodb://localhost:27017/")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((ip_address, port))

standard_data_types = {
    "varchar": "varchar",
    "int": "int",
}


def open_file(json_file_name="Catalog.json"):
    with open(json_file_name) as json_file:
        return json.load(json_file)


def write_json(json_database):
    with open('Catalog.json', 'w') as f:
        json.dump(json_database, f, indent=4)


def check_primary_or_unique_key(attribute_name, attributes_list):
    unique_keys = [key['attributeName'] for key in attributes_list]
    return attribute_name in unique_keys


def create_table_indexes(table_name, nonuniqueKeys, uniqueKeys, primaryKey):
    db = client[used_database]
    collection1 = db[table_name]

    if len(primaryKey) > 0:
        for prim in primaryKey:
            uniqueKeys.remove(prim)
        combined_primary_keys = '+'.join(obj["attributeName"] for obj in primaryKey)
        primarykey_index_name = f"{combined_primary_keys}_{table_name}_uniq_index"

        collection = db[primarykey_index_name]
        mongo_document = {
            "key": "",
            "values": ""
        }
        collection.insert_one(mongo_document)
        collection1.create_index([(combined_primary_keys, pymongo.ASCENDING)], unique=False, name=primarykey_index_name)

    for unique in uniqueKeys:
        index_name = f"{unique['attributeName']}_{table_name}_uniq_index"
        collection = db[index_name]
        mongo_document = {
            "key": "",
            "values": ""
        }

        collection.insert_one(mongo_document)
        collection1.create_index([(unique['attributeName'], pymongo.ASCENDING)], unique=False, name=index_name)

    for nonunique in nonuniqueKeys:
        index_name = f"{nonunique}_{table_name}_nonuniq_index"
        collection = db[index_name]
        mongo_document = {
            "key": "",
            "values": ""
        }
        collection.insert_one(mongo_document)
        collection1.create_index([(nonunique, pymongo.ASCENDING)], unique=False, name=index_name)

    # collection1.drop_index("__id_")

    # msg = "CREATED INDEXES {} FOR TABLE {}".format(new_create_indexes, table_name)
    # serverSocket.sendto(msg.encode(), address)
    # collection.create_index([(uniq_key, pymongo.ASCENDING)], unique=True, name=index_name)

def get_index_fields(fields):
    return []


def insert_into_indexes(table_name, value_dict, prim_key, prim_key_attributes, non_primary_attributes):
    data = open_file()
    db = client[used_database]
    collection = db[table_name]
    existing_indexes = [index_name for index_name in collection.index_information().keys() if
                        index_name != '_id_']

    for auto_generated_index in existing_indexes:
        index_type = auto_generated_index.split("_")[-2]
        fields = auto_generated_index.split("_")[0].split("+")
        new_prim_key = '#'.join(value_dict[obj] for obj in fields)
        collection1 = db[auto_generated_index]
        if collection1.count_documents({'key': {'$ne': ""}}) == 0:
            collection1.delete_one({'key': "", 'values': ""})
        if fields == prim_key_attributes:
            if check_primary_key_uniqueness(collection1, 'key', prim_key):
                mongo_document = {
                    "key": prim_key,
                    "values": non_primary_attributes
                }
                collection1.insert_one(mongo_document)
        elif index_type == "uniq":
            if check_primary_key_uniqueness(collection1, 'key', new_prim_key):
                mongo_document = {
                    "key": new_prim_key,
                    "values": prim_key
                }
                collection1.insert_one(mongo_document)
        elif index_type == "nonuniq":
            if check_primary_key_uniqueness(collection1, 'key', new_prim_key):
                mongo_document = {
                    "key": new_prim_key,
                    "values": prim_key
                }
                collection1.insert_one(mongo_document)
            else:
                existing_doc = collection1.find_one({'key': new_prim_key})
                if existing_doc:
                    updated_values = f"{existing_doc['values']}#{prim_key}"
                    collection1.update_one({'key': new_prim_key}, {'$set': {'values': updated_values}})
                else:
                    # If the document with the non-unique key does not exist, insert a new document
                    mongo_document = {
                        "key": new_prim_key,
                        "values": prim_key
                    }
                    collection1.insert_one(mongo_document)

    # for index in data["databases"][used_database]["tables"][table_name]["indexFiles"]:
    #     index_name = index['indexName']
    #     index_type = index['isUnique'] == '1'
    #     index_attributes = [attr['attributeName'] for attr in index['indexAttributes']]
    #     new_prim_key = '#'.join(value_dict[obj] for obj in index_attributes)
    #     if index_name != table_name:
    #         collection1 = db[index_name]
    #         if index_type:
    #             if check_primary_key_uniqueness(collection1, 'key', new_prim_key):
    #                 mongo_document = {
    #                     "key": new_prim_key,
    #                     "values": prim_key
    #                 }
    #                 collection1.insert_one(mongo_document)
    #         else:
    #             if check_primary_key_uniqueness(collection1, 'key', new_prim_key):
    #                 mongo_document = {
    #                     "key": new_prim_key,
    #                     "values": prim_key
    #                 }
    #                 collection1.insert_one(mongo_document)
    #             else:
    #                 existing_doc = collection1.find_one({'key': new_prim_key})
    #                 if existing_doc:
    #                     updated_values = f"{existing_doc['values']}#{prim_key}"
    #                     collection1.update_one({'key': new_prim_key}, {'$set': {'values': updated_values}})
    #                 else:
    #                     # If the document with the non-unique key does not exist, insert a new document
    #                     mongo_document = {
    #                         "key": new_prim_key,
    #                         "values": prim_key
    #                     }
    #                     collection1.insert_one(mongo_document)


def create_uniq_index(table_name, index_name, uniq_key):
    db = client[used_database]
    collection = db[table_name]

    # index_name = f"{uniq_key}_{table_name}_uniq_index"

    try:
        # Create a unique index on the specified field
        collection.create_index([(uniq_key, pymongo.ASCENDING)], unique=False, name=index_name)

        collection = db[index_name]
        mongo_document = {
            "key": "",
            "values": ""
        }
        collection.insert_one(mongo_document)

        # Update the document with the unique index field
        # collection.update_one({'key': primary_key_value}, {'$set': {uniq_key: primary_key_value}})

        # msg = f"Created and updated unique index for {uniq_key} in table {table_name}."
        # serverSocket.sendto(msg.encode(), address)
    except pymongo.errors.DuplicateKeyError:
        # Handle duplicate key error
        msg = f"Unique key violation. {uniq_key} already exists in table {table_name}."
        serverSocket.sendto(msg.encode(), address)


def create_nonuniq_index(table_name, index_name, nonuniq_key):
    db = client[used_database]
    collection = db[table_name]

    # index_name = f"{nonuniq_key}_{table_name}_uniq_index"

    try:
        # Create a nonunique index on the specified field
        collection.create_index([(nonuniq_key, pymongo.ASCENDING)], unique=False, name=index_name)

        collection = db[index_name]
        mongo_document = {
            "key": "",
            "values": ""
        }
        collection.insert_one(mongo_document)

        # Update the document with the nonunique index field
        # collection.update_one({'key': primary_key_value}, {'$set': {nonuniq_key: primary_key_value}})

        # msg = f"Created and updated nonunique index for {nonuniq_key} in table {table_name}."
        # serverSocket.sendto(msg.encode(), address)
    except pymongo.errors.DuplicateKeyError:
        # Handle duplicate key error
        msg = f"Nonunique key violation. {nonuniq_key} already exists in table {table_name}."
        serverSocket.sendto(msg.encode(), address)


used_database = ""


def use(statement):
    if statement[0] in client.list_database_names():
        global used_database
        used_database = statement[0]
        msg = "NOW USING DATABASE {}".format(statement[0])
        serverSocket.sendto(msg.encode(), address)
    else:
        msg = "DATABASE DOES NOT EXIST"
        serverSocket.sendto(msg.encode(), address)


def parseAttributesForIndex(statement):
    attributes = []
    for attribute in statement:
        if attribute != '(' and attribute != ');' and attribute != ')':
            attributes.append(attribute.strip().replace(',', ''))
    return attributes


def parseAttributes(statement):
    attributes = ''
    for attribute in statement:
        attributes += attribute + ' '
    attributes = attributes[:-2]  # remove first and final paranthesis
    attributes = attributes.split(',')
    return attributes


def create(statement):
    data = open_file()
    if statement[0].lower() == "database":
        database_name = statement[1]
        if database_name not in client.list_database_names():
            if data == {}:
                data = {"databases": {}}
            data["databases"][database_name] = ({"name": database_name, "tables": {}})
            write_json(data)
            db = client[database_name]
            collection = db["local"]
            mongo_document = {
                "key": "",
                "values": ""
            }
            collection.insert_one(mongo_document)
            msg = "CREATED DATABASE {}".format(statement[1])
            serverSocket.sendto(msg.encode(), address)
        else:
            msg = "DATABASE {} ALREADY EXISTS".format(statement[1])
            serverSocket.sendto(msg.encode(), address)
    elif statement[0].lower() == "table":
        if used_database:
            db = client[used_database]
            tableName = statement[1][:-1]
            if tableName not in db.list_collection_names():
                statement = statement[2:]  # remove table and table name from statement
                attributes = parseAttributes(statement)  # separate attributes by comma
                structure = []
                primaryKey = []
                uniqueKeys = []
                nonuniqueKeys = []
                indexAttributes = []
                indexFiles = []
                attributesNames = []
                foreignKeys = []
                foundIndexes = 0
                for attribute in attributes:
                    attribute = attribute.split(' ')
                    if attribute[0] == "":
                        attribute = attribute[1:]  # check for white spaces after comma
                    if "primary" in attribute:  # check for any primary key
                        primaryKey.append({"attributeName": attribute[0]})
                        uniqueKeys.append({"attributeName": attribute[0]})
                        indexAttributes.append({"attributeName": attribute[0]})
                        foundIndexes = 1
                    if "unique" in attribute:  # check for any unique key
                        uniqueKeys.append({"attributeName": attribute[0]})
                    if "not" and "null" in attribute or "primary" in attribute:  # check if attribute value is not null
                        isNull = '0'
                    else:
                        isNull = '1'
                    if '(' in attribute[1]:  # check if there's a declared length
                        length = attribute[1].split('(', 1)[1]
                        length = length[:-1]
                        type = attribute[1].split('(', 1)[0]
                    else:
                        length = "4"
                        type = attribute[1]
                    if type not in standard_data_types:  # check attribute's type
                        msg = "INVALID ATTRIBUTE TYPE: {}".format(type)
                        serverSocket.sendto(msg.encode(), address)
                        return
                    if "references" in attribute:
                        referedTable = attribute[5].split('(')[0]
                        referedAttribute = attribute[5].split('(')[1][:-1]
                        tables = data["databases"][used_database]["tables"]
                        if referedTable not in tables:
                            msg = "TABLE NOT FOUND IN GIVEN DATABASE {}".format(used_database)
                            serverSocket.sendto(msg.encode(), address)
                        else:
                            structure1 = data["databases"][used_database]["tables"][referedTable]["structure"]
                            for attribute1 in structure1:
                                attributesNames.append(attribute1["attributeName"])
                            if referedAttribute not in attributesNames:
                                msg = "ATTRIBUTE NOT FOUND IN GIVEN TABLE {}".format(referedTable)
                                serverSocket.sendto(msg.encode(), address)
                            else:
                                foreignKeys.append({"foreignKey": attribute[0], "refTable": referedTable,
                                                    "refAttribute": referedAttribute})
                    structure.append({"attributeName": attribute[0], "type": type, "length": length, "isNull": isNull})
                    if not check_primary_or_unique_key(attribute[0], uniqueKeys):
                        nonuniqueKeys.append(attribute[0])
                if foundIndexes == 1:  # check if there are declared indexes
                    indexFiles.append({"indexName": tableName, "keyLength": len(tableName), "isUnique": "1",
                                       "indexType": "BTree",
                                       "indexAttributes": indexAttributes})
                table = {"tableName": tableName, "fileName": tableName + ".bin", "rowLength": len(attributes),
                         "structure": structure,
                         "primaryKey": primaryKey,
                         "foreignKeys": foreignKeys,
                         "uniqueKeys": uniqueKeys,
                         "indexFiles": indexFiles}
                data["databases"][used_database]["tables"][tableName] = table
                write_json(data)
                db = client[used_database]
                collection = db[tableName]
                mongo_document = {
                    "key": "",
                    "values": ""
                }
                collection.insert_one(mongo_document)
                create_table_indexes(tableName, nonuniqueKeys, uniqueKeys, primaryKey)
                msg = "CREATED TABLE {}".format(tableName)
                serverSocket.sendto(msg.encode(), address)
            else:
                msg = "TABLE {} ALREADY EXISTS.".format(tableName)
                serverSocket.sendto(msg.encode(), address)
        else:
            msg = "DATABASE NOT SELECTED"
            serverSocket.sendto(msg.encode(), address)
    elif statement[0].lower() == "index":
        if used_database:
            indexType = statement[1]
            indexName = statement[2]
            tableName = statement[4][:-1]
            statement = statement[5:]  # remove index name and table name from statement
            indexFiles = data["databases"][used_database]["tables"][tableName]["indexFiles"]
            structure = data["databases"][used_database]["tables"][tableName]["structure"]
            foundAttributes = 1
            indexAttributes = []
            attributesNames = []
            attributes = parseAttributesForIndex(statement)  # separate attributes by comma

            db = client[used_database]
            collection = db[tableName]
            existing_indexes = [index_name for index_name in collection.index_information().keys() if
                                index_name != '_id_']
            # Check if an index with the same name already exists
            existing_index_names = [idx["indexName"] for idx in indexFiles]

            if f"{indexName}_uniq_index" in existing_indexes or f"{indexName}_nonuniq_index" in existing_indexes:
                msg = "INDEX {} ALREADY EXISTS FOR TABLE {}".format(indexName, tableName)
                serverSocket.sendto(msg.encode(), address)
            else:
                for attribute in structure:
                    attributesNames.append(attribute["attributeName"])
                for attribute in attributes:
                    if attribute[0] == " ":
                        attribute = attribute[1:]  # check for white spaces after comma
                    if attribute not in attributesNames:  # check if given attribute exists
                        msg = "ATTRIBUTE NOT FOUND IN GIVEN TABLE {}".format(attribute)
                        serverSocket.sendto(msg.encode(), address)
                        foundAttributes = 0
                    else:
                        indexAttributes.append({"attributeName": attribute})
                if foundAttributes == 1:
                    primary_key = data["databases"][used_database]["tables"][tableName]["primaryKey"][0][
                        "attributeName"]
                    if "unique" == indexType:
                        create_uniq_index(tableName, indexName, '_'.join(attributes))
                    elif "nonunique" == indexType:
                        create_nonuniq_index(tableName, indexName, '_'.join(attributes))
                    else:
                        msg = "INVALID INDEX TYPE"
                        serverSocket.sendto(msg.encode(), address)

                    indexFiles.append({"indexName": indexName, "keyLength": len(indexName), "isUnique": "1",
                                       "indexType": "BTree",
                                       "indexAttributes": indexAttributes})
                    data["databases"][used_database]["tables"][tableName]["indexFiles"] = indexFiles
                    write_json(data)
                    msg = "CREATED INDEX {}".format(indexName)
                    serverSocket.sendto(msg.encode(), address)
        else:
            msg = "DATABASE NOT SELECTED"
            serverSocket.sendto(msg.encode(), address)

    else:
        msg = "INVALID ATTRIBUTE FOR CREATE COMMAND"
        serverSocket.sendto(msg.encode(), address)


def check_primary_key_uniqueness(collection, primary_key_field, primary_key_value):
    # Check if the primary key value is unique within the given collection.
    existing_key_count = collection.count_documents({primary_key_field: primary_key_value})
    return existing_key_count == 0


def check_referential_integrity(foreign_keys, value_dict, data):
    # Checks if foreign key values exist as primary keys in their respective parent tables.
    for fk in foreign_keys:
        ref_table = fk["refTable"]
        fk_value = value_dict[fk["foreignKey"]]

        ref_table_collection = client[used_database][ref_table]

        fk_value_int = int(fk_value)
        # Now construct the query with the correct field and value
        ref_query = {"key": fk_value_int}

        # Check if there is at least one document that matches the query
        if ref_table_collection.count_documents(ref_query) == 0:
            # If no document is found, the referential integrity check fails
            return False

    # If all foreign key checks pass, return True
    return True


def insert(statement):
    global used_database, serverSocket, client, address
    data = open_file()

    if (statement[0].lower() != "into") or (len(statement) < 3):
        serverSocket.sendto("INVALID INSERT COMMAND".encode(), address)
    else:
        if used_database:
            table_name = statement[1]
            values_str = ' '.join(statement[3:])

            # Split values using both commas and spaces as delimiters
            values = re.split(r'[,\s]+', values_str.strip())
            values = [v.strip() for v in values if v.strip() != ');' and v.strip() != ')' and v.strip() != '(']

            table_structure = data["databases"][used_database]["tables"][table_name]["structure"]
            value_dict = {table_structure[i]["attributeName"]: values[i] for i in range(len(values))}

            if table_name in data["databases"][used_database]["tables"]:
                table_structure = data["databases"][used_database]["tables"][table_name]["structure"]
                primary_key_attributes = data["databases"][used_database]["tables"][table_name]["primaryKey"]

                if len(values) != len(table_structure):
                    msg = "Number of values does not match the table structure."
                    serverSocket.sendto(msg.encode(), address)
                    return

                non_primary_values = []  # List to hold all non-primary attributes
                primary_key_value = None  # Variable to hold the primary key value

                for i in range(len(table_structure)):
                    attribute_name = table_structure[i]["attributeName"]
                    attribute_type = table_structure[i]["type"]
                    is_primary_key = any(attr["attributeName"] == attribute_name for attr in primary_key_attributes)
                    value = values[i]

                    if attribute_type == "int":
                        try:
                            value = int(value)
                        except ValueError:
                            msg = f"Invalid value '{value}' for attribute '{attribute_name}'."
                            serverSocket.sendto(msg.encode(), address)
                            return

                    if is_primary_key:
                        if primary_key_value is None:
                            primary_key_value = str(value)
                        else:
                            primary_key_value += f'${value}'
                    else:
                        non_primary_values.append(str(value))

                if primary_key_value is None:
                    msg = "Primary key value not found."
                    serverSocket.sendto(msg.encode(), address)
                    return

                # Concatenate non-primary key attributes
                non_primary_attributes = '#'.join(non_primary_values)
                foreign_keys = data["databases"][used_database]["tables"][table_name].get("foreignKeys", [])

                # Perform the referential integrity check
                if not check_referential_integrity(foreign_keys, value_dict, data):
                    msg = "Foreign key value does not exist in the referenced primary key."
                    serverSocket.sendto(msg.encode(), address)
                    return

                # Insert data into the master K-V file in the specified format
                master_kv_filename = f"{table_name}_master_kv.txt"
                with open(master_kv_filename, "a") as master_kv_file:
                    # Create a dictionary for the key-value entry
                    kv_entry = {
                        'Key': primary_key_value,
                        'Value': non_primary_attributes
                    }
                    # Convert the dictionary to a JSON-formatted string
                    kv_entry_string = json.dumps(kv_entry)
                    # Write the JSON-formatted string to the file
                    master_kv_file.write(kv_entry_string + "\n")

                # Insert data into MongoDB
                db = client[used_database]
                collection = db[table_name]

                mongo_document = {
                    "key": primary_key_value,
                    "values": non_primary_attributes
                }

                # If no documents with non-empty 'key' are found, then delete the document with empty 'key' and 'values'
                if collection.count_documents({'key': {'$ne': ""}}) == 0:
                    collection.delete_one({'key': "", 'values': ""})

                if check_primary_key_uniqueness(collection, 'key', primary_key_value):
                    collection.insert_one(mongo_document)
                    insert_into_indexes(table_name, value_dict, primary_key_value, [attr["attributeName"] for attr in primary_key_attributes], non_primary_attributes)
                    msg = f"Values inserted into table {table_name}."
                    serverSocket.sendto(msg.encode(), address)
                else:
                    # The primary key is not unique
                    msg = f"Insert failed. Primary key already exists."
                    serverSocket.sendto(msg.encode(), address)

            else:
                msg = f"Table {table_name} does not exist in the current database."
                serverSocket.sendto(msg.encode(), address)
        else:
            msg = "Database not selected. Use 'use' command to select a database."
            serverSocket.sendto(msg.encode(), address)


def drop(statement):
    data = open_file()
    global used_database
    if statement[0].lower() == "database":
        db_data = data["databases"].get(statement[1], None)
        if db_data:
            db = statement[1]
            tables_from_db = db_data["tables"]
            if not tables_from_db:
                client.drop_database(db)  # Drop the MongoDB database
                del data["databases"][db]
                write_json(data)
                msg = "DROPPED DATABASE {}".format(db)
                serverSocket.sendto(msg.encode(), address)
                if used_database == db:
                    used_database = ""
            else:
                msg = "DATABASE {} CANNOT BE DELETED, DELETE THE COLLECTIONS TO COMPLETE THE ACTION.".format(
                    statement[1])
                serverSocket.sendto(msg.encode(), address)
        else:
            msg = "DATABASE DOES NOT EXIST"
            serverSocket.sendto(msg.encode(), address)
    elif statement[0].lower() == "table":
        if used_database:
            table_name = statement[1]
            table = data["databases"][used_database]["tables"].get(table_name, None)
            if table:
                # Check for foreign key references to this table
                db = client[used_database]
                index_information = db[table_name].index_information()
                indexes = [key for key in index_information.keys()]
                if "_id_" in indexes:
                    indexes.remove("_id_")
                if len(indexes) > 0:
                    indexesString = "index" if len(indexes) == 1 else "indexes"
                    msg = "Cannot delete table \"{}\" because it contains the \"{}\" \"{}\"".format(table_name,
                                                                                                    indexesString,
                                                                                                    ', '.join(indexes))
                    serverSocket.sendto(msg.encode(), address)
                    return

                for other_table_name, other_table in data["databases"][used_database]["tables"].items():
                    if other_table_name != table_name:
                        for foreign_key in other_table.get("foreignKeys", []):
                            if foreign_key.get("refTable") == table_name:
                                msg = "Cannot delete table \"{}\" because it is referenced as a foreign key " \
                                      "in table \"{}\"".format(table_name, other_table_name)
                                serverSocket.sendto(msg.encode(), address)
                                return  # Exit the function without deleting the table

                if client[used_database][table_name].count_documents({}) > 0:
                    msg = "Cannot drop table \"{}\" because it contains data.".format(table_name)
                    serverSocket.sendto(msg.encode(), address)
                    return  # Exit the function without deleting the table if it contains data
                # No foreign key references, safe to delete
                del data["databases"][used_database]["tables"][table_name]
                write_json(data)
                client[used_database][table_name].drop()
                msg = "DROPPED TABLE {}".format(table_name)
                serverSocket.sendto(msg.encode(), address)
            else:
                msg = "TABLE DOES NOT EXIST"
                serverSocket.sendto(msg.encode(), address)
        else:
            msg = "DATABASE NOT SELECTED"
            serverSocket.sendto(msg.encode(), address)


# def check_referential_integrity_for_delete(key_attr, key_val, data, used_database):
#     # Loop through all tables in the database
#     for table_name, table_info in data["databases"][used_database]["tables"].items():
#         # If the current table contains the key as a primary key, skip it
#         primary_keys = table_info.get('primaryKey', [])
#         if any(pk['attributeName'] == key_attr for pk in primary_keys):
#             continue  # Skip the table where the key is the primary key
#
#         # Check if the table has foreign keys and iterate through them
#         for fk in table_info.get('foreignKeys', []):
#             # Check if the foreign key references the key_attr (primary key in another table)
#             if fk['refAttribute'] == key_attr:
#                 # Connect to the MongoDB database and collection
#                 db = client[used_database]
#                 collection = db[table_name]
#
#                 # Check if any document in the collection contains the key_val as a foreign key value
#                 # Build a query to check for the foreign key value
#                 query = {fk['foreignKey']: key_val}
#                 if collection.count_documents(query) > 0:
#                     # If key_val is being used as a foreign key, return a message indicating a violation
#                     return f"Cannot delete: The key {key_val} is being referenced as a foreign key in table '{table_name}', under the attribute '{fk['foreignKey']}'."
#
#     # If no references are found, return None indicating it's safe to delete
#     return None


def delete(statement):
    global used_database, serverSocket, client, address
    data = open_file()  # Function to read the database structure from file.

    if (statement[0].lower() != "from") or (len(statement) < 5):
        serverSocket.sendto("INVALID DELETE COMMAND".encode(), address)
        return

    if used_database:
        table_name = statement[1]
        key_attr = statement[3]  # This is the attribute name of the key
        key_val = statement[5].strip(' ;')  # This is the value of the key, stripping potential semicolon

        # Check if the table exists
        if table_name in data["databases"][used_database]["tables"]:
            db = client[used_database]
            collection = db[table_name]
            table_structure = data["databases"][used_database]["tables"][table_name]["structure"]

            # Find the attribute in the structure to determine its type
            attribute_type = next((attr["type"] for attr in table_structure if attr["attributeName"] == key_attr), None)

            if attribute_type is None:
                msg = f"Attribute {key_attr} not found in the table structure."
                serverSocket.sendto(msg.encode(), address)
                return

            # Cast key_val to the appropriate type based on attribute_type
            if attribute_type == "int":
                try:
                    key_val = int(key_val)
                except ValueError:
                    msg = f"Invalid value for integer key: {key_val}"
                    serverSocket.sendto(msg.encode(), address)
                    return
            elif attribute_type == "varchar":
                key_val = str(key_val)  # Ensuring that the key_val is a string
            # Add additional type checks if necessary

            # referential_integrity_message = check_referential_integrity_for_delete(key_attr, key_val, data,
            #                                                                        used_database)
            # if referential_integrity_message:
            #     # If the function returned a message, there's a referential integrity violation
            #     serverSocket.sendto(referential_integrity_message.encode(), address)
            #     return

            # Perform the delete operation
            deletion_result = collection.delete_many({'key': key_val})

            if deletion_result.deleted_count > 0:
                msg = f"Deleted {deletion_result.deleted_count} documents from table {table_name}."
                serverSocket.sendto(msg.encode(), address)
            else:
                msg = "No documents matched the query."
                serverSocket.sendto(msg.encode(), address)
        else:
            msg = f"Table {table_name} does not exist in the current database."
            serverSocket.sendto(msg.encode(), address)
    else:
        msg = "Database not selected. Use 'use' command to select a database."
        serverSocket.sendto(msg.encode(), address)


print("Server Up")

while True:
    clientData, address = serverSocket.recvfrom(bufferSize)

    clientData = clientData.decode().split(" ")

    if clientData[0].lower() in ["create", "drop", "use", "insert", "delete"]:
        func = locals()[clientData[0]]
        del clientData[0]
        func(clientData)
    else:
        print("INVALID COMMAND")
