from ctypes import c_byte, c_char, c_ubyte, c_ushort, c_uint, Structure, Union


SECTOR_SIZE = 4096
NUM_SECTORS_PER_SLOT = 14

def GetSectionLength(section_number):
    # https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III)#Section_ID
    
    section_length = 3968 # 0xF80
    
    if section_number == 0:
        section_length = 3884
    elif section_number == 4:
        section_length == 3848
    elif section_number == 13:
        section_length = 2000
    elif section_number >= 0xFFFF or section_number < 0:
        section_length = 0
    
    return section_length

class SaveChunk(Structure):
    _fields_ = \
    (
        ('data', c_ubyte * (SECTOR_SIZE - 128)),
        ('_padding', c_ubyte * (128 - 12)),
        ('ID', c_ushort),
        ('checksum', c_ushort),
        ('magic', c_uint),
        ('save_index', c_uint),
    )
    
    def GetLength(self):
        return GetSectionLength(self.ID)
    
    def Validate(self):
        return not self.GetError()
        
    def CalculateChecksum(self):
        buflen = self.GetLength()
        buf = self.data
        
        chk = 0
        i = 0
        while i < buflen:
            val =  buf[i + 0]
            val |= buf[i + 1] << 8
            val |= buf[i + 2] << 16
            val |= buf[i + 3] << 24
            chk += val
            i += 4
        
        chk = (chk + (chk >> 16)) & 0xFFFF
        
        return chk
    
    def GetError(self):
        if self.magic != 0x08012025:
            return 1
        
        chk = self.CalculateChecksum()
        
        if chk != self.checksum:
            return 2
        
        return 0
    
    def Regenerate(self):
        self.magic = 0x08012025
        self.checksum = self.CalculateChecksum()
        
        assert self.Validate()
