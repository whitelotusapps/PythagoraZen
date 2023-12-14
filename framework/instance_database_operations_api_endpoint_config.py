import inspect
import logging

from pymongo import MongoClient

from framework.logging_handler import PythagoraZenLogger


class ZendeskInstanceDatabaseOperationsMongoDB:
    def __init__(self, subdomain, collection_name):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.subdomain = subdomain
        self.client = MongoClient(
            "mongodb://localhost:27017/"
        )  # Assuming MongoDB is running locally
        self.db = self.client[subdomain]

        # logging.info(f"MONGODB CLASS: {self.db}")

        self.zendesk_subdomain = subdomain

        if collection_name:
            self.collection = self.db[collection_name]
            logging.info(f"MONGODB CLASS: {self.collection}")

    def list_available_collections(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        return self.db.list_collection_names()

    def insert_collection_data(self, data):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if not isinstance(data, list):
            raise TypeError(f"{type(data)} data must be a list")

        if not data:
            logging.warning(f"{data} data is empty. No documents will be inserted.")
            return

        try:
            logging.info(f"INSERTING DATA INTO COLLECTION: {self.collection}")
            # self.delete_many()
            self.collection.insert_many(data)
        except Exception as e:
            error_message = str(e)
            logging.error(f"Error inserting {data} data: {error_message}")
            raise

    def delete_many(self, query={}):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Delete many documents from the specified collection based on the given query
        self.collection.delete_many(query)
        self.collection.delete_many({"id": None})

    def query_collection(self, query={}, projection=None):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.debug(f"Query: {query}")
        logging.debug(f"Projection: {projection}")
        return list(self.collection.find(query, projection))

    """
    def query_collection(self, query={}):
        return list(self.collection.find(query))
    """

    def create_indexes(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if "id" in self.collection.index_information():
            self.collection.create_index("id", unique=True)

    def close_connection(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # Close the MongoDB connection
        self.client.close()
