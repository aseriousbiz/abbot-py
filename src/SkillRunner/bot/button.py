class Button(object):
    """
    A button presented to the user.

    :var title: The title displayed on the button.
    :var args: The arguments to pass back to this skill when the button is clicked.
    :var style: (optional) The style to apply to the button. Allowed values are 'default', 'primary', and 'danger'. Use 'primary' and 'danger' sparingly.
    """
    def __init__(self, title, args=None, style="default"):
        self.title = title
        self.arguments = args if args is not None else title
        self.style = style

    def toJSON(self):
        return {
            "Title": self.title,
            "Arguments": self.arguments,
            "Style": self.style
        }