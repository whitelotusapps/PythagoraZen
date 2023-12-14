import inspect

# database_operations.py
import logging
import os
import sqlite3

from framework.logging_handler import PythagoraZenLogger


class CredentialDatabaseOperations:
    def __init__(self):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.subdomain_folder = "config_data/credentials"
        self.db_path = os.path.join(
            self.subdomain_folder, "zendesk_instance_credentials.db"
        )
        # Create the subdomain folder if it doesn't exist
        os.makedirs(self.subdomain_folder, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS zendesk_info 
                         (id INTEGER PRIMARY KEY, subdomain TEXT, api_user_email_address TEXT, 
                          api_key TEXT)"""
        )
        self.conn.commit()

    def add_instance(self, subdomain, api_user_email_address, api_key):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.c.execute(
            """INSERT INTO zendesk_info (subdomain, api_user_email_address, api_key)
                          VALUES (?, ?, ?)""",
            (subdomain, api_user_email_address, api_key),
        )
        self.conn.commit()

    def update_instance(
        self, old_subdomain, new_subdomain, api_user_email_address, api_key
    ):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.c.execute(
            """UPDATE zendesk_info 
                          SET subdomain=?, api_user_email_address=?, api_key=?
                          WHERE subdomain=?""",
            (new_subdomain, api_user_email_address, api_key, old_subdomain),
        )
        self.conn.commit()

    def fetch_instances(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.c.execute(
            "SELECT subdomain, api_user_email_address, api_key FROM zendesk_info"
        )
        return self.c.fetchall()

    def fetch_credentials(self, subdomain):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        self.c.execute(
            "SELECT subdomain, api_user_email_address, api_key FROM zendesk_info WHERE subdomain = ?",
            (subdomain,),
        )
        credentials = self.c.fetchone()

        return (
            {
                "subdomain": credentials[0],
                "api_user_email": credentials[1],
                "api_key": credentials[2],
            }
            if credentials
            else {}
        )

    def delete_instance(self, subdomain):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.info("This is the delete_instance function")
        self.c.execute("DELETE FROM zendesk_info WHERE subdomain = ?", (subdomain,))
        self.conn.commit()
