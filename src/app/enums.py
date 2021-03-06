class UserPrivacy:
    CLOSE = 0
    OPEN = 1
    valid_value = [CLOSE, OPEN]

    @classmethod
    def is_valid(cls, privacy):
        try:
            return int(privacy) in cls.valid_value
        except ValueError:
            return False
