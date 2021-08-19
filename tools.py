import crawler

def is_positive_integer(s):
    if s.isdigit() and ( len(s) == 1 or s[0] != '0'):
        return True
    else:
        return False

class BotArguments:
    def __init__(self, arguments):
        self.arguments = arguments
    def __getitem__(self, index):
        try:
            return_argument = self.arguments[index]
        except IndexError:
            return ''
        return return_argument
