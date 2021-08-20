def is_positive_integer(s):
    if s.isdigit() and ( len(s) == 1 or s[0] != '0'):
        return True
    else:
        return False
