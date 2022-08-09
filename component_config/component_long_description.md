# Bulkgate

This application is used for sending SMS and Viber messages using [bulkgate api](https://www.bulkgate.com/en/).


## Input

Input must be a table with 3 columns:

 - `number` - phone number to which message will be send - must include country code (ex: 420123123123)
 - `text` - text which will be send
 - `timestamp` - `0` for message to be sent right away or [unix timestamp](https://en.wikipedia.org/wiki/Unix_time)/[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) for message to be sent at a specific time

## Credentials

Credentials used for authentification:

 - `Application ID`
 - `Application token`

Can be created as per [here](https://help.bulkgate.com/docs/en/api-administration.html).

## Settings

Additional settings for message sending:

 - `Message type` - can be either `Transactional` or `Promotional` depending on the purpose of the message. Be aware that as per [documentation](https://help.bulkgate.com/docs/en/difference-promotional-transactional-sms.html#transactional-sms) **it is *strictly prohibited* to exploit transactional SMS for promotional/marketing uses. It must be used for notification purposes only - as an SMS notification.**
 - `Sender ID` - [sender ID profile](https://help.bulkgate.com/docs/en/sender-id-profile.html)
 - `Send to Viber?` - if `true` message will be send to `viber` primarly and fallback to `SMS` if the provided phone number does not have `viber` account. If `false` message will be send only via `SMS`
 - `Viber sender` - sender name which will be shown in `viber` as the sender of a message (this field is mandatory if `Send to Viber?` is `true`

## Output

As an output, 3 tables are returned.
 - `stats` - contains information about the sent messages in total
 - `messages` - contains information about each sent message
 - `messages_parts` - contains information about message parts for each message