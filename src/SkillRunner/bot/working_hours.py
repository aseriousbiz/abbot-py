class WorkingHours(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def contains(self, time):
        return time.start.compare(self.start) >= 0 and time.end.compare(self.end) <= 0

    def humanize(self):
        return 'from {} to {}'.format(self.start, self.end)

    @classmethod
    def from_json(cls, json):
        if json is None:
            return None
        return cls(json.get('Start'), json.get('End'))


class Time(object):
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

    def __str__(self):
        return '{}:{}'.format(self.hour, self.minute)

    @classmethod
    def parse(cls, value):
        if value is None:
            return None
        # Split value into hour and minute
        hour, minute = value.split(':')
        return cls(hour, minute)

    # Compares this Time to another Time.
    # returns -1 if the this time is less than the other time, 0 if they are equal, 1 if this time is greater than the other time.
    def compare(self, other):
        if self.hour < other.hour:
            return -1
        elif self.hour > other.hour:
            return 1
        else:
            if self.minute < other.minute:
                return -1
            elif self.minute > other.minute:
                return 1
            else:
                return 0