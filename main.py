# This is a sample Python script.
from pymongo import MongoClient


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script
    # Connect to the MongoDB server
    client = MongoClient("mongodb+srv://zimbruflorin5:NKMPyAJBWP8Ildn0@sgbd.cdzpzuw.mongodb.net/?retryWrites=true&w=majority")

    # Select a database
    db = client["florin"]

    # Select a collection
    collection = db["test"]

    # Insert a document with an acknowledged write concern
    # result = collection.insert_one({"key": "value"})

    # Check if the write was acknowledged
    # if result.acknowledged:
    #     print("Write acknowledged and data is persisted.")
    # else:
    #     print("Write might not be acknowledged or persisted.")

    # Close the MongoDB connection when done
    client.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
