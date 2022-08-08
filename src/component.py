"""
Template Component main class.

"""
# import csv
import sys
import logging
from dataclasses import dataclass
import pandas as pd
import requests
# from datetime import datetime

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# configuration variables
KEY_CREDENTIALS = 'credentials'
KEY_CREDENTIALS_APPLICATION_ID = '#application_id'
KEY_CREDENTIALS_APPLICATION_TOKEN = '#application_token'

KEY_SETTINGS = 'settings'
KEY_SETTINGS_SENDER_ID = 'sender_id'
KEY_SETTINGS_MESSAGE_TYPE = 'message_type'
KEY_SETTINGS_VIBER = 'viber'
KEY_SETTINGS_VIBER_SENDER = 'viber_sender'

PROMOTIONAL_URL = "https://portal.bulkgate.com/api/2.0/advanced/promotional"
TRANSACTIONAL_URL = "https://portal.bulkgate.com/api/2.0/advanced/transactional"

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = []
REQUIRED_IMAGE_PARS = []


@dataclass
class Credentials:
    application_id: str
    application_token: str


@dataclass
class Settings:
    sender_id: str
    message_type: str
    viber: bool
    viber_sender: str


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

        _credentials_object = self._parse_credentials_parameters()
        _settings_object = self._parse_settings_parameters()

        _data_in = self._parse_table()

        _url = self._get_url(_settings_object)
        _body = self._get_body(_credentials_object, _settings_object)

        self._send_messages(_url, _body, _data_in)

    def _parse_credentials_parameters(self):
        credentials = self.configuration.parameters.get(KEY_CREDENTIALS, {})
        if credentials == {}:
            logging.exception("Credentials configuration not specified.")
            sys.exit(1)
        try:
            credentials_obj = Credentials(
                credentials[KEY_CREDENTIALS_APPLICATION_ID],
                credentials[KEY_CREDENTIALS_APPLICATION_TOKEN]
                )
        except KeyError as e:
            logging.exception(f"Missing mandatory field {e} in credentials.")
            sys.exit(1)
        return credentials_obj

    def _parse_settings_parameters(self):
        settings = self.configuration.parameters.get(KEY_SETTINGS, {})
        if settings == {}:
            logging.exception("Settings configuration not specified.")
            sys.exit(1)
        try:
            settings_obj = Settings(
                settings[KEY_SETTINGS_SENDER_ID],
                settings[KEY_SETTINGS_MESSAGE_TYPE],
                settings[KEY_SETTINGS_VIBER],
                settings[KEY_SETTINGS_VIBER_SENDER]
                )

            if settings_obj.viber and settings_obj.viber_sender == '':
                logging.exception(
                    f"Missing mandatory field {KEY_SETTINGS_VIBER_SENDER} in settings. "
                    f"Please specify {KEY_SETTINGS_VIBER_SENDER} for Viber."
                    )
                sys.exit(1)

        except KeyError as e:
            logging.exception(f"Missing mandatory field {e} in settings.")
            sys.exit(1)

        return settings_obj

    def _parse_table(self):
        in_tables = self.configuration.tables_input_mapping

        if len(in_tables) == 0:
            logging.exception('There is no table specified on the input mapping! You must provide one input table!')
            exit(1)
        elif len(in_tables) > 1:
            logging.exception(
                'There is more than one table specified on the input mapping! You must provide one input table!')
            exit(1)

        table = in_tables[0]

        logging.info(f'Processing input table: {table["destination"]}')
        df = pd.read_csv(f'{self.tables_in_path}/{table["destination"]}', dtype=str)

        if df.empty:
            logging.exception(f'Input table {table["destination"]} is empty!')
            exit(1)

        return df

    def _get_url(self, settings):
        if settings.message_type == 'Promotional':
            return PROMOTIONAL_URL
        return TRANSACTIONAL_URL

    def _get_body(self, credentials, settings):
        channels = {}
        if settings.viber:
            channels['viber'] = {"sender": settings.viber_sender}
        channels['sms'] = {"sender_id": "gProfile", "sender_id_value": settings.sender_id}

        admins = []
        if len(settings.admins) > 0:
            admins = settings.admins

        return {"application_id": credentials.application_id,
                "application_token": credentials.application_token,
                "number": [],
                "channel": channels,
                "admins": admins
                }

    def _send_messages(self, url, body, data):
        """
        Send messages to the specified recipients
        """
        timestamps = data.timestamp.unique()

        for time in timestamps:
            number = []
            for message in data.loc[data.timestamp == time].to_dict('records'):
                number.append(
                    {"number": message['number'], "text": message['text']}
                )
            body['number'] = number

            if time != "0":
                body['schedule'] = time

            response = requests.post(url, json=body)
            stats = response.json()['data']['total']['status']
            logging.info(stats)


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
