"""
Template Component main class.

"""
import csv
from dataclasses import dataclass
from datetime import datetime
import logging
import pandas as pd
import requests
import copy

from typing import List, Dict

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# credentials variables
KEY_CREDENTIALS = 'credentials'
KEY_CREDENTIALS_APPLICATION_ID = '#application_id'
KEY_CREDENTIALS_APPLICATION_TOKEN = '#application_token'

# settings variables
KEY_SETTINGS = 'settings'
KEY_SETTINGS_SENDER_ID = 'sender_id'
KEY_SETTINGS_MESSAGE_TYPE = 'message_type'
KEY_SETTINGS_UNICODE = "sms_unicode"
KEY_SETTINGS_DUPLICATES_CHECK = "duplicates_check"
KEY_SETTINGS_CHANNEL = 'send_channel'
KEY_SETTINGS_VIBER_SENDER = 'viber_sender'

# set urls
PROMOTIONAL_URL = "https://portal.bulkgate.com/api/2.0/advanced/promotional"


@dataclass
class Credentials:
    """
    Credentials dataclass.
    """
    application_id: str
    application_token: str


@dataclass
class Settings:
    """
    Settings dataclass.
    """
    sender_id: str
    message_type: str
    send_channel: str
    viber_sender: str
    unicode: bool
    duplicates_check: str


class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Main execution code
        """

        # Parse credentials
        _credentials_object = self._parse_credentials_parameters()
        _settings_object = self._parse_settings_parameters()

        # Parse table
        _data_in = self._parse_table()

        # Get url and body
        _url = self._get_url()
        _body = self._get_body(_credentials_object, _settings_object)

        if not _data_in.empty:
            self._create_tables_definitions()

            # Send messages
            self._send_messages(_url, _body, _data_in)

            # Close files and manifest data
            self._close_and_manifest_files()

    def _parse_credentials_parameters(self):
        """
        Parses credentials parameters from the configuration.
        """

        # Get credentials
        credentials = self.configuration.parameters.get(KEY_CREDENTIALS, {})
        if credentials == {}:
            raise UserException("Credentials configuration not specified.")

        try:
            # Set credentials object
            credentials_obj = Credentials(
                credentials[KEY_CREDENTIALS_APPLICATION_ID],
                credentials[KEY_CREDENTIALS_APPLICATION_TOKEN]
            )
        except KeyError as e:
            raise UserException(f"Missing mandatory field {e} in credentials.") from e

        return credentials_obj

    def _parse_settings_parameters(self):
        """
        Parses settings parameters from the configuration.
        """

        # Get settings
        settings = self.configuration.parameters.get(KEY_SETTINGS, {})
        if settings == {}:
            raise UserException("Settings configuration not specified.")

        try:
            # Set settings object
            settings_obj = Settings(
                settings[KEY_SETTINGS_SENDER_ID],
                settings[KEY_SETTINGS_MESSAGE_TYPE],
                settings.get(KEY_SETTINGS_CHANNEL, "viber"),
                settings[KEY_SETTINGS_VIBER_SENDER],
                settings.get(KEY_SETTINGS_UNICODE, False),
                settings.get(KEY_SETTINGS_DUPLICATES_CHECK)
            )

            # Validate settings
            if settings_obj.send_channel in ["viber", "viber_sms"] and settings_obj.viber_sender == '':
                raise UserException(
                    f"Missing mandatory field {KEY_SETTINGS_VIBER_SENDER} in settings. "
                    f"Please specify {KEY_SETTINGS_VIBER_SENDER} for Viber."
                )
            if settings_obj.duplicates_check and settings_obj.duplicates_check not in ["same_text", "same_number",
                                                                                       "null"]:
                raise UserException("Value of Duplicates Check must be one of : [\"same_text\", \"same_number\"]")

        except KeyError as e:
            raise UserException(f"Missing mandatory field {e} in settings.") from e

        return settings_obj

    def _parse_table(self):
        """
        Parses the data table.
        """

        # Get tables configuration
        in_tables = self.get_input_tables_definitions()

        if len(in_tables) == 0:
            raise UserException('There is no table specified on the input mapping! You must provide one input table!')
        elif len(in_tables) > 1:
            raise UserException(
                'There is more than one table specified on the input mapping! You must provide one input table!')

        # Get table
        table = in_tables[0]

        # Get table data
        logging.info(f'Processing input table: {table.name}')
        df = pd.read_csv(f'{table.full_path}', dtype=str)

        # Return error if there is no data
        if df.empty:
            logging.info(f'Input table {table.name} is empty!')

        return df

    @staticmethod
    def _get_url() -> str:
        """
        Returns the url for the request.
        """
        return PROMOTIONAL_URL

    @staticmethod
    def _get_body(credentials: Credentials, settings: Settings) -> Dict:
        """
        Returns the body for the request.
        """

        # Set channels
        channels = {}
        if settings.send_channel in ["viber", "viber_sms"]:
            channels['viber'] = {"sender": settings.viber_sender}

        if settings.send_channel in ["sms", "viber_sms"]:
            channels['sms'] = {
                "sender_id": "gProfile",
                "sender_id_value": str(settings.sender_id),
                "unicode": settings.unicode
            }

        body = {"application_id": credentials.application_id,
                "application_token": credentials.application_token,
                "number": [],
                "channel": channels}

        if settings.duplicates_check:
            body["duplicates_check"] = settings.duplicates_check

        return body

    @staticmethod
    def create_groups_of_dataframes_that_share_the_same_column_values(data: pd.DataFrame, columns: List) -> List[
        pd.DataFrame]:  # noqa
        return [sub_df for group, sub_df in data.groupby(columns, dropna=False)]

    @staticmethod
    def get_texts_from_dataframe(df: pd.DataFrame) -> List[Dict]:
        return [{"number": row.number, "text": row.text} for index, row in df.iterrows()]

    @staticmethod
    def _get_non_changing_param_from_dataframe(df: pd.DataFrame, param_name: str):
        """
        This method gets a specific column from a dataframe, where the column value should be the same for each row.
        If a specific row contains a different value for the column a UserException is raised
        """
        param = None
        for index, row in df.iterrows():
            if param and param != row[param_name]:
                raise UserException(f"Grouping of {param_name} have failed, it is not possible to send a single"
                                    f" request with multiple texts that contain different {param_name}s")
            param = row[param_name]
        return param

    def _send_messages(self, url: str, body: Dict, data: pd.DataFrame) -> None:
        """
        Send messages to the specified recipients
        """

        if 'button_caption' not in data.columns:
            if "viber" in body["channel"]:
                logging.warning("button_caption column is missing in data, not adding buttons to viber messages")
            data['button_caption'] = None

        if 'button_url' not in data.columns:
            if "viber" in body["channel"]:
                logging.warning("button_url column is missing in data, not adding buttons to viber messages")
            data['button_url'] = None

        # Create button_object column
        data['button_object'] = data.apply(lambda x: {'caption': x['button_caption'], 'url': x['button_url']}, axis=1)

        # Create add_button column that is a boolean indicator if a button has valid params
        data['add_button'] = data['button_caption'].notnull() & data['button_url'].notnull()

        # Each request has to have the same timestamp/schedule as well as the same button, as the button is defined in
        # the channel. Each number+text that has the same schedule and same button can be sent in a single request
        # with the number and text in the "number" parameter of the body. The below code is used to create a list of
        # dataframes that share the same button and schedule.
        send_groups = self.create_groups_of_dataframes_that_share_the_same_column_values(data, ['button_url',
                                                                                                'button_caption',
                                                                                                "timestamp"])

        for group in send_groups:
            final_body = copy.deepcopy(body)

            final_body['number'] = self.get_texts_from_dataframe(group)
            timestamp = self._get_non_changing_param_from_dataframe(group, "timestamp")

            button = self._get_non_changing_param_from_dataframe(group, "button_object")
            add_button = self._get_non_changing_param_from_dataframe(group, "add_button")

            if "viber" in final_body["channel"] and add_button:
                final_body["channel"]['viber']["button"] = button

            # Set schedule if present
            if timestamp != "0":
                final_body['schedule'] = timestamp

            response = requests.post(url, json=final_body)

            # Return error if the request fails
            if response.status_code != 200:
                raise UserException(
                    f'There was an error calling Bulkgate API due to {response.reason}. {response.text}')

            self._save_response(response.json())

    def _create_tables_definitions(self):
        """
        Creates the tables definitions for output tables.
        """

        # Create tables definitions
        self._stats_table = self.create_out_table_definition('stats.csv', incremental=True, primary_key=['timestamp'])
        self._messages_table = self.create_out_table_definition(
            'messages.csv', incremental=True, primary_key=['message_id'])
        self._messages_parts_table = self.create_out_table_definition(
            'messages_parts.csv', incremental=True, primary_key=['part_id'])
        self._invalid_number_errors_table = self.create_out_table_definition(
            'invalid_number_errors.csv', incremental=True, primary_key=['number', 'timestamp'])

        # Open stats file, set headers, writer and write headers
        self._stats_file = open(self._stats_table.full_path, 'wt', encoding='UTF-8', newline='')
        stats_fields = [
            'timestamp', 'sent', 'accepted', 'scheduled',
            'error', 'blacklisted', 'invalid_number', 'invalid_sender'
        ]
        self._stats_writer = csv.DictWriter(self._stats_file, fieldnames=stats_fields)
        self._stats_writer.writeheader()

        # Open messages file, set headers, writer and write headers
        self._messages_file = open(self._messages_table.full_path, 'wt', encoding='UTF-8', newline='')
        messages_fields = ['message_id', 'status', 'number', 'channel', 'timestamp']
        self._messages_writer = csv.DictWriter(self._messages_file, fieldnames=messages_fields)
        self._messages_writer.writeheader()

        # Open messages parts file, set headers, writer and write headers
        self._messages_parts_file = open(self._messages_parts_table.full_path, 'wt', encoding='UTF-8', newline='')
        messages_parts_fields = ['part_id', 'message_id']
        self._messages_parts_writer = csv.DictWriter(self._messages_parts_file, fieldnames=messages_parts_fields)
        self._messages_parts_writer.writeheader()

        self._invalid_number_errors_file = open(self._invalid_number_errors_table.full_path, 'wt', encoding='UTF-8',
                                                newline='')
        _invalid_number_errors_fields = ["number", "status", "code", "error", "detail", "channel", "timestamp"]
        self._invalid_number_errors_writer = csv.DictWriter(self._invalid_number_errors_file,
                                                            fieldnames=_invalid_number_errors_fields)
        self._invalid_number_errors_writer.writeheader()

    def _save_response(self, response: Dict) -> None:
        """
        Save response to the output table
        """
        current_time = datetime.now().isoformat()

        # Parse stats data
        stats = response['data']['total']['status']
        stats['timestamp'] = current_time

        # Load stats data
        self._stats_writer.writerow(stats)

        # Parse messages data and load
        for message in response['data']['response']:
            message['timestamp'] = current_time
            if message.get("status") == "invalid_number":
                self._invalid_number_errors_writer.writerow(message)
            elif message.get("status") == "invalid_sender":
                raise UserException("Invalid Sender")
            else:
                # Load messages parts data
                if message.get('part_id'):
                    for part in message['part_id']:
                        self._messages_parts_writer.writerow({
                            'part_id': part,
                            'message_id': message['message_id']
                        })

                message.pop('part_id', None)
                self._messages_writer.writerow(message)

    def _close_and_manifest_files(self):
        """
        Close and manifest files
        """
        # Close files
        self._stats_file.close()
        self._messages_file.close()
        self._messages_parts_file.close()
        self._invalid_number_errors_file.close()

        # Manifest files
        self.write_manifests(
            [self._stats_table, self._messages_table, self._messages_parts_table, self._invalid_number_errors_table])


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
