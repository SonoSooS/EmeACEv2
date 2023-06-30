from ctypes import c_ubyte, c_ushort, c_uint, Structure, Union
from .globals import PLAYER_NAME_LENGTH, POKEMON_NAME_LENGTH


MAX_MON_MOVES = 4
NUM_SUBSTRUCT_BYTES = 12

SUBSTRUCT_CASE = \
(
    (0,1,2,3),
    (0,1,3,2),
    (0,2,1,3),
    (0,3,1,2),
    (0,2,3,1),
    (0,3,2,1),
    (1,0,2,3),
    (1,0,3,2),
    (2,0,1,3),
    (3,0,1,2),
    (2,0,3,1),
    (3,0,2,1),
    (1,2,0,3),
    (1,3,0,2),
    (2,1,0,3),
    (3,1,0,2),
    (2,3,0,1),
    (3,2,0,1),
    (1,2,3,0),
    (1,3,2,0),
    (2,1,3,0),
    (3,1,2,0),
    (2,3,1,0),
    (3,2,1,0),
)

class PokemonSubstruct0(Structure):
    _fields_ = \
    (
        ('species', c_ushort),
        ('heldItem', c_ushort),
        ('experience', c_uint),
        ('ppBonuses', c_ubyte),
        ('friendship', c_ubyte),
        ('_filler', c_ushort),
    )
    
class PokemonSubstruct1(Structure):
    _fields_ = \
    (
        ('moves', c_ushort * MAX_MON_MOVES),
        ('pp', c_ubyte * MAX_MON_MOVES),
    )

class PokemonSubstruct2(Structure):
    _fields_ = \
    (
        ('hpEV', c_ubyte),
        ('attackEV', c_ubyte),
        ('defenseEV', c_ubyte),
        ('speedEV', c_ubyte),
        ('spAttackEV', c_ubyte),
        ('spDefenseEV', c_ubyte),
        ('cool', c_ubyte),
        ('beauty', c_ubyte),
        ('cute', c_ubyte),
        ('smart', c_ubyte),
        ('tough', c_ubyte),
        ('sheen', c_ubyte),
    )

class PokemonSubstruct3(Structure):
    _fields_ = \
    (
        ('pokerus', c_ubyte),
        ('metLocation', c_ubyte),
        
        ('metLevel', c_ushort, 7),
        ('metGame', c_ushort, 4),
        ('pokeball', c_ushort, 4),
        ('otGender', c_ushort, 1),
        
        ('hpIV', c_uint, 5),
        ('attackIV', c_uint, 5),
        ('defenseIV', c_uint, 5),
        ('speedIV', c_uint, 5),
        ('spAttackIV', c_uint, 5),
        ('spDefenseIV', c_uint, 5),
        ('isEgg', c_uint, 1),
        ('abilityNum', c_uint, 1),
        
        ('coolRibbon', c_uint, 3),
        ('beautyRibbon', c_uint, 3),
        ('cuteRibbon', c_uint, 3),
        ('smartRibbon', c_uint, 3),
        ('toughRibbon', c_uint, 3),
        ('championRibbon', c_uint, 1),
        ('winningRibbon', c_uint, 1),
        ('victoryRibbon', c_uint, 1),
        ('artistRibbon', c_uint, 1),
        ('effortRibbon', c_uint, 1),
        ('marineRibbon', c_uint, 1),
        ('landRibbon', c_uint, 1),
        ('skyRibbon', c_uint, 1),
        ('countryRibbon', c_uint, 1),
        ('nationalRibbon', c_uint, 1),
        ('earthRibbon', c_uint, 1),
        ('worldRibbon', c_uint, 1),
        ('unusedRibbons', c_uint, 4),
        ('eventLegal', c_uint, 1),
    )

class PokemonSubstructUnion(Union):
    _anonymous_ = ('type0', 'type1', 'type2', 'type3')
    _fields_ = \
    (
        ('type0', PokemonSubstruct0),
        ('type1', PokemonSubstruct1),
        ('type2', PokemonSubstruct2),
        ('type3', PokemonSubstruct3),
        ('raw_chksum', c_ushort * (NUM_SUBSTRUCT_BYTES // 2))
    )

class PokemonSubstructSecure(Union):
    _fields_ = \
    (
        ('data', PokemonSubstructUnion * 4),
        ('raw_crypt', c_uint * (NUM_SUBSTRUCT_BYTES * 4 // 4)),
    )
    
    @staticmethod
    def GetStructIndex(index: int, personality: "int | c_uint") -> int:
        num: int = personality if isinstance(personality, int) else personality.value
        
        return SUBSTRUCT_CASE[num % len(SUBSTRUCT_CASE)][index]
    
    def DoCrypto(self, personality: "int | c_uint", otId: "int | c_uint"):
        num1: int = personality if isinstance(personality, int) else personality.value
        num2: int = otId if isinstance(otId, int) else otId.value
        
        num = num1 ^ num2
        
        for i in range(len(self.raw_crypt)):
            self.raw_crypt[i] = self.raw_crypt[i] ^ num
    
    def Checksum(self):
        return sum(sum(x.raw_chksum) for x in self.data)
    

class BoxPokemon(Structure):
    _fields_ = \
    (
        ('personality', c_uint),
        ('otId', c_uint),
        ('nickname', c_ubyte * POKEMON_NAME_LENGTH),
        ('language', c_ubyte),
        
        ('isBadEgg', c_ubyte, 1),
        ('hasSpecies', c_ubyte, 1),
        ('isEgg', c_ubyte, 1),
        ('_unused', c_ubyte, 5),
        
        ('otName', c_ubyte * PLAYER_NAME_LENGTH),
        
        ('scribbles', c_ubyte),
        ('checksum', c_ushort),
        ('_unknown', c_ushort),
        
        ('secure', PokemonSubstructSecure),
    )
    
    @classmethod
    def FromView(cls, view: memoryview, offs: int = 0):
        return cls.from_buffer(view[offs:offs+80])
    
    def FixChecksum(self):
        self.checksum = self.secure.Checksum()
    
    def GetSub0(self) -> PokemonSubstruct0:
        return self.secure.data[self.secure.GetStructIndex(self.personality, 0)].type0
    def GetSub1(self) -> PokemonSubstruct1:
        return self.secure.data[self.secure.GetStructIndex(self.personality, 1)].type1
    def GetSub2(self) -> PokemonSubstruct2:
        return self.secure.data[self.secure.GetStructIndex(self.personality, 2)].type2
    def GetSub3(self) -> PokemonSubstruct3:
        return self.secure.data[self.secure.GetStructIndex(self.personality, 3)].type3
    
    def __enter__(self):
        self.secure.DoCrypto(self.personality, self.otId)
        pass
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.secure.DoCrypto(self.personality, self.otId)
        return False

class Pokemon(Structure):
    _anonymous_ = ('box',)
    _fields_ = \
    (
        ('box', BoxPokemon),
        ('status', c_uint),
        ('level', c_ubyte),
        ('mail', c_ubyte),
        ('hp', c_ushort),
        ('maxHP', c_ushort),
        ('attack', c_ushort),
        ('defense', c_ushort),
        ('speed', c_ushort),
        ('spAttack', c_ushort),
        ('spDefense', c_ushort),
    )
    
    def __enter__(self):
        self.box.__enter__()
        pass
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.box.__exit__(exc_type, exc_value, traceback)
