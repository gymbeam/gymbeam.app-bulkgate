## Input

Input should be a table with 5 columns:

 - `number` - phone number to which message will be send - must include country code (ex: 420123123123)
 - `text` - text which will be send
 - `timestamp` - `0` for message to be sent right away or [unix timestamp](https://en.wikipedia.org/wiki/Unix_time)/[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) for message to be sent at a specific time
 - `button_caption` - Caption for the [Button object](https://help.bulkgate.com/docs/en/http-advanced-promotional-v2.html#button-object-parameters-table) to be sent with a viber message. Can be null for sms. button_url must also be provided
 - `button_url` - URL for the [Button object](https://help.bulkgate.com/docs/en/http-advanced-promotional-v2.html#button-object-parameters-table) to be sent with a viber message. Can be null for sms. button_caption must also be provided
 
## Credentials

Credentials used for authentification:

 - `Application ID`
 - `Application token`

Can be created as per [here](https://help.bulkgate.com/docs/en/api-administration.html).

## Settings

Additional settings for message sending:

 - `Message type` - can be either `Transactional` or `Promotional` depending on the purpose of the message. Be aware that as per [documentation](https://help.bulkgate.com/docs/en/difference-promotional-transactional-sms.html#transactional-sms) **it is *strictly prohibited* to exploit transactional SMS for promotional/marketing uses. It must be used for notification purposes only - as an SMS notification.** 
 - `Sender ID` - [sender ID profile](https://help.bulkgate.com/docs/en/sender-id-profile.html)
 - `Sending Option?` - Determines which channels will be used for sending the message: "viber" for viber only, "sms" for sms only, "viber_sms" for viber and sms as backup
 - `Viber sender` - Sender name which will be shown in `viber` as the sender of a message (this field is mandatory if `send_options` is `viber_sms` or `viber`
 - `SMS Unicode` - If set to true, messages via sms will be sent in unicode (characters with diacritics will be sent properly) .
 - `Duplicates Check` - Select 'same_text' to prevent sending duplicate messages to the same phone number. Disable the possibility to send a message with either the same or different text to the same number with 'same_number'. If 'null' no duplicates will be removed.
