Bulkgate
=============

Bulkgate is a SaaS solution for message sending. The service allows you to send customized transactional or promotional message via SMS or Viber.

Prerequisites
=============

Get the [register application](https://portal.bulkgate.com/application/) and create [sender profile](https://portal.bulkgate.com/sms-settings/).

Configuration
=============

Application ID (`#application_id`)
-------
Application ID for Bulkgate advanced API. More inormation can be found [here](https://help.bulkgate.com/docs/en/api-administration.html#what-is-application-id).

Application token (`#application_token`)
-------
Application token for Bulkgate advanced API. More information can be found [here](https://help.bulkgate.com/docs/en/api-tokens.html#what-is-an-api-token).

Message type (`message_type`)
-------
Message type which determines which URL will be used. Currently, can only be  `Promotional` 

Sender ID (`sender_id`)
-------
Sender ID which will be used to send message. More information can be found [here](https://help.bulkgate.com/docs/en/sender-id-profile.html)

SMS Unicode (`sms_unicode`)
-------
If set to true, messages via sms will be sent in unicode (characters with diacritics will be sent properly) .

Duplicates Check (`duplicates_check`)
-------
Select 'same_text' to prevent sending duplicate messages to the same phone number. Disable the possibility to send a message with either the same or different text to the same number with 'same_number'. If 'null' no duplicates will be removed.

Sending Channel (`send_channel`)
-------
Determines which channels will be used for sending the message: "viber" for viber only, "sms" for sms only, "viber_sms" for viber and sms as backup

Viber sender (`viber_sender`)
-------
Sender name which will be shown in `viber` as the sender of a message (this field is mandatory if `send_options` is `viber_sms` or `viber`

Input
======
Input must be a table with 5 columns:

 - `number` - phone number to which message will be send - must include country code (ex: 420123123123)
 - `text` - text which will be send
 - `timestamp` - `0` for message to be sent right away or [unix timestamp](https://en.wikipedia.org/wiki/Unix_time)/[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) for message to be sent at a specific time
 - `button_caption` - Caption for the [Button object](https://help.bulkgate.com/docs/en/http-advanced-promotional-v2.html#button-object-parameters-table) to be sent with a viber message. Can be null for sms. button_url must also be provided
 - `button_url` - URL for the [Button object](https://help.bulkgate.com/docs/en/http-advanced-promotional-v2.html#button-object-parameters-table) to be sent with a viber message. Can be null for sms. button_caption must also be provided
 
Output
======

As an output, 4 tables are returned.
 - `stats` - contains information about the sent messages in total
 - `messages` - contains information about each sent message
 - `messages_parts` - contains information about message parts for each message
 - `invalid_number_errors` - contains information about numbers that were not able to have messages sent to them because they were invalid

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to
your custom path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following
command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/gymbeam/gymbeam.app-bulkgate.git gymbeam.app-bulkgate
cd gymbeam.app-bulkgate
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~