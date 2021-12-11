from SkillRunner.bot.button import Button
from SkillRunner.bot.message_options import MessageOptions


class ReplyClient(object):
    """
    Used to send replies back to chat. If we have a valid ConversationReference, then we send 
    the reply as a direct message. Rreplies are sent asynchronously at the time bot.reply is
    called. Otherwise replies are returned synchrously in the response to the request that
    calls this skill.
    """
    def __init__(self, api_client, conversation_reference, skill_id, responses):
        self._api_client = api_client
        self._conversation_reference = conversation_reference
        self._skill_id = skill_id
        self._reply_url = "/reply"
        self._responses = responses

    def reply(self, response: str, message_options: MessageOptions):
        """
        Send a reply. If direct_message is True, then the reply is sent as a direct message to the caller.
        
        Args:
            response (str): The response to send back to chat.
        """
        if self._conversation_reference:
            body = self.__create_reply_payload(response, message_options)
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))

    def reply_with_image(self, image: str, response: str, title: str, title_url: str, color: str, message_options: MessageOptions):
        if self._conversation_reference:
            body = self.__create_reply_payload(response, message_options, attachments=[
                {
                    "Buttons": [],
                    "ImageUrl": image,
                    "Title": title,
                    "TitleUrl": title_url,
                    "Color": color
                }
            ])
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))

    def reply_with_buttons(self, response: str, buttons: list[Button], buttons_label: str, image_url: str, title: str, color: str, message_options: MessageOptions):
        """
        Sends a reply with a set of buttons. Clicking a button will call back into this skill.

        Args:
            response (str): The message to send as a response.
            buttons (list[Button]): The set of buttons to display (Maximum 6).
            buttons_label (str): The text that serves as a label for the set of buttons (optional).
            image_url (str): An image to render before the set of buttons (optional).
            title (str): A title to render (optional).
            color (str): The color to use for the sidebar (Slack Only) in hex (ex. #3AA3E3) (optional).
        """
        if self._conversation_reference:
            body = self.__create_reply_payload(response, message_options, attachments=[
                {
                    "Buttons": [b.toJSON() for b in buttons],
                    "ButtonsLabel": buttons_label,
                    "ImageUrl": image_url,
                    "Title": title,
                    "Color": color
                }
            ])
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))

    def reply_later(self, response: str, delay_in_seconds: int, message_options: MessageOptions):
        """
        Reply after a delay.

        Args:
            response (str): The response to send back to chat.
            delay_in_seconds (int): The number of seconds to delay before sending the response.
        """
        if self._conversation_reference:
            body = self.__create_reply_payload(response, message_options, schedule=delay_in_seconds)
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))

    def __create_reply_payload(self, response: str, message_options: MessageOptions, attachments: list = [], schedule: int = 0):
        return {
            "SkillId": self._skill_id,
            "Message": str(response),
            "ConversationReference": self._conversation_reference,
            "Options": message_options.toJSON(),
            "Attachments": attachments,
            "Schedule": schedule,
        }