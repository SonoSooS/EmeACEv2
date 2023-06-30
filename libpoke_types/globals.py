from ctypes import *

POKEMON_NAME_LENGTH = 10
PLAYER_NAME_LENGTH = 7


class Coords16(Structure):
    _fields_ = \
    (
        ('x', c_short),
        ('y', c_short),
    )

class WarpData(Structure):
    _fields_ = \
    (
        ('mapGroup', c_byte),
        ('mapNum', c_byte),
        ('warpId', c_byte),
        ('_padding', c_byte),
        ('x', c_short),
        ('y', c_short),
    )
