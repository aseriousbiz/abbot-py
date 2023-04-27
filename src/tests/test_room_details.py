import unittest
import json

from SkillRunner.bot.room_details import RoomDetails

class RoomDetailsTest(unittest.TestCase):
    def test_from_json(self):
        details_json = {
  "BotIsMember": 'true',
  "ConversationTrackingEnabled": 'true',
  "ResponseSettings": {
    "ResponseTime": {
      "Warning": "365.00:00:00",
      "Deadline": "720.00:00:00"
    },
    "FirstResponders": [
      {
        "Id": "U0000000004",
        "UserName": "kermit",
        "Name": "kermit",
        "Location": {
          "TimeZone": "America/Los_Angeles"
        },
        "WorkingHours": {
          "Start": "09:15:00",
          "End": "18:00:00",
          "Duration": "08:45:00"
        }
      }
    ],
    "EscalationResponders": [
      {
        "Id": "U012LKJFG0P",
        "UserName": "haacked",
        "Name": "haacked",
        "Email": "phil@aseriousbusiness.com",
        "Location": {
          "TimeZone": "America/Los_Angeles",
          "Coordinate": {
            "Latitude": 47.6120759,
            "Longitude": -122.1112721
          },
          "FormattedAddress": "Bellevue, WA 98008, USA"
        },
        "WorkingHours": {
          "Start": "09:00:00",
          "End": "18:00:00",
          "Duration": "09:00:00"
        }
      }
    ]
  },
  "DefaultResponseSettings": {
    "ResponseTime": {
      "Warning": "365.00:00:00",
      "Deadline": "720.00:00:00"
    },
    "FirstResponders": [
      {
        "Id": "U012LKJFG0P",
        "UserName": "haacked",
        "Name": "haacked",
        "Email": "phil@aseriousbusiness.com",
        "Location": {
          "TimeZone": "America/Los_Angeles",
          "Coordinate": {
            "Latitude": 47.6120759,
            "Longitude": -122.1112721
          },
          "FormattedAddress": "Bellevue, WA 98008, USA"
        },
        "WorkingHours": {
          "Start": "09:00:00",
          "End": "18:00:00",
          "Duration": "09:00:00"
        }
      },
      {
        "Id": "U0000000004",
        "UserName": "kermit",
        "Name": "kermit",
        "Location": {
          "TimeZone": "America/Los_Angeles"
        },
        "WorkingHours": {
          "Start": "09:15:00",
          "End": "18:00:00",
          "Duration": "08:45:00"
        }
      },
      {
        "Id": "UTEST000001",
        "UserName": "The Bride",
        "Name": "The Bride",
        "Location": {
          "TimeZone": "America/Los_Angeles"
        },
        "WorkingHours": {
          "Start": "09:15:00",
          "End": "18:00:00",
          "Duration": "08:45:00"
        }
      }
    ],
    "EscalationResponders": [
      {
        "Id": "U0000000006",
        "UserName": "neo",
        "Name": "neo",
        "Location": {
          "TimeZone": "America/Los_Angeles"
        },
        "WorkingHours": {
          "Start": "18:00:00",
          "End": "20:04:36",
          "Duration": "02:04:36"
        }
      },
      {
        "Id": "UTEST0000010",
        "UserName": "Tyrion",
        "Name": "Tyrion",
        "Location": {
          "TimeZone": "America/Los_Angeles"
        },
        "WorkingHours": {
          "Start": "09:15:00",
          "End": "18:00:00",
          "Duration": "08:45:00"
        }
      }
    ]
  },
  "Metadata": {
    "CompanyName": "Serious Business",
    "CompanyType": "Rad",
    "CompanyId": "42"
  },
  "Id": "C03FXF26BK2",
  "Name": "haacked-dev-test-2"
}
        details = RoomDetails.from_json(details_json)
        self.assertEqual("C03FXF26BK2", details.id)
        self.assertEqual("365.00:00:00", details.response_settings.response_time.warning)
        self.assertEqual(1, len(details.response_settings.first_responders))

if __name__ == '__main__':
    unittest.main()