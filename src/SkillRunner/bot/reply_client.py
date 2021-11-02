import logging

class ReplyClient(object):
    def __init__(self, api_client, conversation_reference, skill_id, responses):
        self._api_client = api_client
        self._conversation_reference = conversation_reference
        self._skill_id = skill_id
        self._reply_url = "/reply"
        logging.info("Reply URL: %s", self._reply_url)

        self._responses = responses


    def reply(self, response, direct_message=False):
        """
        Send a reply. If direct_message is True, then the reply is sent as a direct message to the caller.
        
        Args:
            response (str): The response to send back to chat.
        """
        if self._conversation_reference:
            body = {
                "SkillId": self._skill_id,
                "Message": str(response),
                "ConversationReference": self._conversation_reference,
                "DirectMessage": direct_message
            }
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))


    def reply_with_image(self, image, response, title, title_url, color):
        if self._conversation_reference:
            body = {
                "SkillId": self._skill_id,
                "Message": str(response),
                "ConversationReference": self._conversation_reference,
                "Attachments": [
                    {
                        "Buttons": [],
                        "ImageUrl": image,
                        "Title": title,
                        "TitleUrl": title_url,
                        "Color": color
                    }
                ]
            }
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))


    def reply_with_buttons(self, response, buttons, buttons_label=None, image_url=None, title=None, color=None):
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
            body = {
                "SkillId": self._skill_id,
                "Message": str(response),
                "ConversationReference": self._conversation_reference,
                "Attachments": [
                    {
                        "Buttons": [b.toJSON() for b in buttons],
                        "ButtonsLabel": buttons_label,
                        "ImageUrl": image_url,
                        "Title": title,
                        "Color": color
                    }
                ]
            }
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))


    def reply_later(self, response, delay_in_seconds):
        """
        Reply after a delay.

        Args:
            response (str): The response to send back to chat.
            delay_in_seconds (int): The number of seconds to delay before sending the response.
        """
        if self._conversation_reference:
            body = {
                "SkillId": self._skill_id,
                "Message": str(response),
                "ConversationReference": self._conversation_reference,
                "Schedule": delay_in_seconds
                }
            self._api_client.post(self._reply_url, body)
        else:
            self._responses.append(str(response))