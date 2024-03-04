import enum


class TwitchResStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_F = 2
    UNAUTH = 3
    ERROR = 4
