import base64
import inspect
import logging

import requests
from PyQt5.QtWidgets import QApplication

from framework.logging_handler import PythagoraZenLogger


class ZendeskApiPaginator:
    def __init__(
        self,
        zendesk_subdomain,
        zendesk_api_user_email,
        zendesk_api_key,
        endpoint,
        per_page=100,
    ):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        # self.base_url = f"https://{zendesk_subdomain}.zendesk.com/api/v2"
        self.base_url = f"https://{zendesk_subdomain}.zendesk.com"
        self.endpoint = endpoint
        self.per_page = per_page
        self.data = []

        if endpoint:
            # Encode credentials for basic authentication
            api_string = f"{zendesk_api_user_email}/token:{zendesk_api_key}"
            self.base64_api_auth = str(base64.b64encode(api_string.encode("utf-8")))[
                2:-1
            ]

            # Create an instance of the status window
            # self.status_window = StatusWindow(endpoint)
            # self.status_window.show()

    def fetch_all_data(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        if not self.endpoint:
            return self.data

        try:
            url_count = 1
            url = f"{self.base_url}{self.endpoint}"
            logging.info(f"{url_count}. {url}\n")

            headers = {"Authorization": f"Basic {self.base64_api_auth}"}

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # print(f"SUCCESS: {response.status_code}\n")
            # print(f"RESPONSE:\n{json.dumps(response.json(), indent=4)}")

            response_json = response.json()
            main_key = next(iter(response_json), None)

            # Check if the data after main_key is a dictionary
            data_after_main_key = response_json.get(main_key, {})

            if isinstance(data_after_main_key, dict):
                # If it's a dictionary, insert the entire dictionary as a single document
                self.data.append(data_after_main_key)
            else:
                # If it's not a dictionary, extend the list (or handle as needed)
                self.data.extend(data_after_main_key)

            # self.status_window.update_status(f"PROCESSING {self.endpoint} REQUEST\n\n")
            # self.status_window.update_status(f"{url_count}. {url}\n")

            while response_json.get("next_page") is not None or response_json.get(
                "meta", {}
            ).get("has_more"):
                url_count += 1

                if "next_page" in response_json:
                    url = response_json["next_page"]
                elif "meta" in response_json and response_json["meta"].get("has_more"):
                    after_cursor = response_json["meta"]["after_cursor"]
                    url = f"{self.base_url}/{self.endpoint}.json?page[after]={after_cursor}&page[size]={self.per_page}"

                # self.status_window.update_status(f"{url_count}. {url}\n")
                logging.info(f"{url_count}. {url}\n")

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                response_json = response.json()
                main_key = next(iter(response_json), None)

                # Check if the data after main_key is a dictionary
                data_after_main_key = response_json.get(main_key, {})

                if isinstance(data_after_main_key, dict):
                    self.data.append(data_after_main_key)
                else:
                    self.data.extend(data_after_main_key)

            # Close the status window once data fetching is complete
            # self.status_window.close()
            # print(f"SELF DATA:\n{json.dumps(self.data, indent=4)}")
            return self.data

        except requests.exceptions.RequestException as e:
            error_message = str(e)
            logging.error(f"REQUEST ERROR: {error_message}")
            # You might want to log or handle the error accordingly
            raise  # Re-raise the exception after printing details


if __name__ == "__main__":
    logging.debug(f"{inspect.currentframe().f_code.co_name}")
    app = QApplication([])
    app.exec_()
