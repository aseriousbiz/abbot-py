import logging
from .api_result import ApiResult
import jsonpickle

class Signaler(object):
    """
    Not to be confused with SignalR, use this to raise signals by calling the
    signal api endpoint https://ab.bot/api/skills/{id}/signal
    """
    def __init__(self, api_client, skill_message):
        self._skill_info = skill_message.get('SkillInfo')
        self._runner_info = skill_message.get('RunnerInfo')
        self._signal_info = skill_message.get('SignalInnfo')
        self._api_client = api_client

    def signal(self, name, args):
        """
        Raises a signal from the skill with the specified name and arguments.
        :param name: The name of the signal to send.
        :param data: The arguments to pass to the skills that are subscribed to this signal.
        :return: a result indicating success or failure
        """
        logging.info(f"Sending signal from skill: {self._skill_info.get('SkillName')}")

        is_root = self._signal_info is None
        conversation_reference = self._runner_info.get('ConversationReference')
        conversation_reference = jsonpickle.encode(conversation_reference) if conversation_reference else None

        skill_info = self._skill_info
        runner_info = self._runner_info

        data = {
            "Name": name,
            "Arguments": args,
            "ConversationReference": conversation_reference,
            "Room": skill_info.get('Room'),
            "RoomId": skill_info.get('RoomId'),
            "SenderId": runner_info.get('MemberId'),
            "Source": {
                "AuditIdentifier": runner_info.get('AuditIdentifier'),
                "SkillName": skill_info.get('SkillName'),
                "SkillUrl": skill_info.get('SkillUrl'),
                "Arguments": skill_info.get('Arguments'),
                "Mentions": skill_info.get('Mentions'),
                "SignalEvent": self._signal_info,
                # Only set these if this is a root source (aka isRoot = true)
                "IsChat" : skill_info.get('IsChat') if is_root else None,
                "IsInteraction": skill_info.get('IsInteraction') if is_root else None,
                "IsPatternMatch": skill_info.get('Pattern') is not None,
                "IsRequest": skill_info.get('IsRequest') if is_root else None,
                "Pattern": skill_info.get('Pattern'), # This could only be populated by a root skill source.
                "Request": skill_info.get('Request')  # This could only be populated by a root skill source.
            }
        }

        return ApiResult(self._api_client.post('/signal', data))