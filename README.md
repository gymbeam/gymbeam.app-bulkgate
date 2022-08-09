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
Message type which determines which URL will be used. Can be either `Transactional` or `Promotional` depending on the purpose of the message. Be aware that as per [documentation](https://help.bulkgate.com/docs/en/difference-promotional-transactional-sms.html#transactional-sms) **it is *strictly prohibited* to exploit transactional SMS for promotional/marketing uses. It must be used for notification purposes only - as an SMS notification.**

Sender ID (`sender_id`)
-------
Sender ID which will be used to send message. More information can be found [here](https://help.bulkgate.com/docs/en/sender-id-profile.html)

Send to Viber? (`viber`)
-------
Determines if message will be primarly sent to `Viber` and fallbacks to `SMS`.

Viber sender (`viber_sender`)
-------
Sender name which will be shown in `viber` as the sender of a message (this field is mandatory if `Send to Viber?` is `true`

Input
======
Input must be a table with 3 columns:

 - `number` - phone number to which message will be send - must include country code (ex: 420123123123)
 - `text` - text which will be send
 - `timestamp` - `0` for message to be sent right away or [unix timestamp](https://en.wikipedia.org/wiki/Unix_time)/[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) for message to be sent at a specific time
 
Output
======

As an output, 3 tables are returned.
 - `stats` - contains information about the sent messages in total
 - `messages` - contains information about each sent message
 - `messages_parts` - contains information about message parts for each message

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