import logging
import inspect
from framework.logging_handler import PythagoraZenLogger


class PipelineOperations:
    def __init__(
        self,
        user_collection,
        organization_collection,
        group_collection,
        custom_role_collection,
        zendesk_subdomain,
    ):
        self.pythagorazen_logger = PythagoraZenLogger()
        self.pythagorazen_logger.configure_logging()
        logging.debug(f"{inspect.currentframe().f_code.co_name}")                
        self.user_collection = user_collection
        self.organization_collection = organization_collection
        self.group_collection = group_collection
        self.custom_role_collection = custom_role_collection
        self.zendesk_subdomain = zendesk_subdomain


    def update_user_data(self):
        logging.debug(f"{inspect.currentframe().f_code.co_name}")
        logging.info(f"pipeline subdomain: {self.zendesk_subdomain}")
        logging.info(f"user_collection: {self.user_collection}")
        logging.info(f"organization_collection: {self.organization_collection}")

        # Get all users from the user collection
        users = list(self.user_collection.find())

        modified_users = []

        # Look up organization name for each user
        for user in users:
            organization_id = user.get("organization_id")
            organization_name = "No Organization"  # Default value

            if organization_id:
                organization = self.organization_collection.find_one(
                    {"id": organization_id}
                )
                if organization:
                    organization_name = organization.get("name")

            default_group_id = user.get("default_group_id")
            default_group_name = "None"

            if default_group_id:
                default_group = self.group_collection.find_one({"id": default_group_id})
                if default_group:
                    default_group_name = default_group.get("name")

            custom_role_id = user.get("custom_role_id")
            custom_role_name = "None"

            if custom_role_id:
                custom_role = self.custom_role_collection.find_one(
                    {"id": custom_role_id}
                )
                if custom_role:
                    custom_role_name = custom_role.get("name")

            if organization_id or default_group_id or custom_role_id:
                logging.info(f"USER: {user.get('name')}")
                logging.info(f"\tORG : {organization_id}")
                logging.info(f"\tGRP : {default_group_id}")
                logging.info(f"\tCRN : {custom_role_id}\n")

            # custom_role_id
            # tags (this is a ist)

            # Add organization_name and url to the original user record
            user["custom_role_name"] = custom_role_name
            user["default_group_name"] = default_group_name
            user["organization_name"] = organization_name
            user[
                "url"
            ] = f"https://{self.zendesk_subdomain}.zendesk.com/agent/users/{user['id']}"

            modified_users.append(user)

        return modified_users
