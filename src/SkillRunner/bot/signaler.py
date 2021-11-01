import logging
from .api_result import ApiResult
import jsonpickle
from .urls import get_skill_api_url
from . import apiclient

class Signaler(object):
    """
    Not to be confused with SignalR, use this to raise signals by calling the
    signal api endpoint https://ab.bot/api/skills/{id}/signal
    """
    def __init__(self, skill_id, user_id, api_token, timestamp, skill_message):
        self.skill_id = skill_id
        self.skill_info = skill_message.get('SkillInfo')
        self.runner_info = skill_message.get('RunnerInfo')
        self.signal_info = skill_message.get('SignalInnfo')
        self.request_uri = get_skill_api_url(skill_id) + '/signal'
        if self.request_uri.startswith("https://localhost"):
            self.verify_ssl = False
        else:
            self.verify_ssl = True
        self.api_client = apiclient.ApiClient(self.request_uri, user_id, api_token, timestamp)


    def signal(self, name, args):
        """
        Raises a signal from the skill with the specified name and arguments.
        :param name: The name of the signal to send.
        :param data: The arguments to pass to the skills that are subscribed to this signal.
        :return: a result indicating success or failure
        """
        logging.info("Sending signal to skill: %s", self.skill_id)

        is_root = self.signal_info is None
        conversation_reference = self.runner_info.get('ConversationReference')
        conversation_reference = jsonpickle.encode(conversation_reference) if conversation_reference else None

        data = {
            "Name": name,
            "Arguments": args,
            "ConversationReference": conversation_reference,
            "Room": self.skill_info.get('Room'),
            "RoomId": self.skill_info.get('RoomId'),
            "SenderId": self.runner_info.get('MemberId'),
            "Source": {
                "AuditIdentifier": self.runner_info.get('AuditIdentifier'),
                "SkillName": self.skill_info.get('SkillName'),
                "SkillUrl": self.skill_info.get('SkillUrl'),
                "Arguments": self.skill_info.get('Arguments'),
                "Mentions": self.skill_info.get('Mentions'),
                # Only set these if this is a root source (aka isRoot = true)
                "IsChat" : is_root and self.skill_info.get('IsChat'),
                "IsInteraction": is_root and self.skill_info.get('IsInteraction'),
                "IsPatternMatch": is_root and self.skill_info.get('Pattern') is not None,
                "IsRequest": is_root and self.skill_info.get('IsRequest'),
                "Pattern": is_root and self.skill_info.get('Pattern'),
                "Request": is_root and self.skill_info.get('Request'),
                "SignalEvent": is_root and self.signal_info,
            }
        }

        logging.info(data)
        return ApiResult(self.api_client.post(self.request_uri, data))