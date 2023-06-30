from libpoke import Savefile, SelectBestIndex
import struct
from ctypes import cast

from libpoke_types.poke import BoxPokemon, Pokemon, PokemonSubstruct0

# Could be argv[0]
#SAVEFILE_NAME = "pokecontest.sav"
SAVEFILE_NAME = "pokeace - Copy.sav"
# Couild be argv[1]
PAYLOAD_NAME = "payload.bin"
# Could be argv[2]
SAVEFILE_OUT_NAME = "pokeace.sav"



SAVEBLOCK_MOVE_RANGE = 128

SAVEBLOCK_2_START = 0x02024A54
SAVEBLOCK_1_START = 0x02025A00
SAVEDATA_PC_START = 0x02029808

GLITCH_ADDR_1 = 0x0206FEFE # 0x202FEFE
GLITCH_ADDR_2 = 0x02030169

EWRAM_SIZE = 256 * 1024
EWRAM_BITS = EWRAM_SIZE - 1


def insert_into(dst, offs, src):
    srclen = len(src)
    dst[offs:offs+srclen] = src

def create_offs(addr):
    offs = (addr & EWRAM_BITS) - (SAVEDATA_PC_START & EWRAM_BITS)
    offs = offs + Savefile.PC_BUFFER_ENTRY_SIZE + 128
    offs = offs - (offs % Savefile.PC_BUFFER_ENTRY_SIZE)
    
    return offs

# dstoffs - pcdata-relative target
def create_jumper(pcdata, dstoffs, srcoffs, type):
    opc = 0xEAFFFFFE - ((Savefile.PC_BUFFER_ENTRY_SIZE * 2) // 4)
    opc -= (srcoffs - dstoffs) // 4
    
    if type == 2:
        # Add jump gadget
        # 03 B0       (ADD SP, #12 (Thumb))
        # 01 BC       (POP {r0} (Thumb))
        # 86 46 00 00 (MOV LR, r0 (Thumb))
        # 78 47 00 00 (BX PC (Thumb))
        # 00 00 00 00 (silly NOP)
        # F6 F7 FF EA (B . - 0x2020)
        payload = \
            b'\x04\xB0' +\
            b'\x01\xBC' +\
            b'\x86\x46\x00\x00' +\
            b'\x78\x47\x00\x00' +\
            b'\x00\x00\x00\x00' +\
            struct.pack('<I', opc)
    else:
        # Add jump gadget
        # 78 47 00 00 (BX PC (Thumb))
        # 00 00 00 00 (silly NOP)
        # F6 F7 FF EA (B . - 0x2020)
        payload = b'\x78\x47\xFF\x00\x00\x00\x00\x00' + struct.pack('<I', opc)
        #'\xF6\xF7\xFF\xEA'
    
    insert_into(pcdata, srcoffs, payload)

def do_exploit(pcdata, fn_exploit):
    
    dstoffs = Savefile.PC_SCREEN_FULL_BYTES
    
    srcoffs1 = create_offs(GLITCH_ADDR_1)
    srcoffs2 = create_offs(GLITCH_ADDR_2)
    
    insert_into(pcdata, 0, b'\x00' * srcoffs2)
    
    create_jumper(pcdata, dstoffs, srcoffs1, 1)
    create_jumper(pcdata, dstoffs, srcoffs2, 2)
    
    with open(fn_exploit, "rb") as f:
        payload = f.read()
    
    assert dstoffs + len(payload) < len(pcdata), "PC buffer overflow"
    
    insert_into(pcdata, dstoffs, payload)
    
    pass

def do_party_test(partydata):
    
    asd = (Pokemon * 6).from_buffer(partydata)
    
    mon: Pokemon = asd[1]
    with mon:
        box: BoxPokemon = mon.box
        sub0: PokemonSubstruct0 = box.GetSub0()
        sub1: PokemonSubstruct0 = box.GetSub1()
        sub2: PokemonSubstruct0 = box.GetSub2()
        sub3: PokemonSubstruct0 = box.GetSub3()
        
        box.personality = 1
        box.isBadEgg = False
        box.isEgg = False
        sub3.isEgg = False
        
        #print("species", hex(sub0.species).upper())
        sub0.species = 0x425A
        
        insert_into(box.nickname, 0, b'\xCE\xBB\xCD\xB5\x53\x54\xFF')
        #box.nickname[4] = 0xFF
        box.otName[4] = 0xFF
        
        mon.box.FixChecksum()
    
    pass

def main():
    savebuf1 = None
    savebuf2 = None
    savebuf_rest = None
    
    argv = ['lol.py', SAVEFILE_NAME, PAYLOAD_NAME, SAVEFILE_OUT_NAME]
    
    with open(argv[1], "rb") as f:
        savebuf1 = bytearray(f.read(Savefile.DATA_SIZE))
        savebuf2 = bytearray(f.read(Savefile.DATA_SIZE))
        savebuf_rest = f.read()
    
    save1 = Savefile(savebuf1)
    save2 = Savefile(savebuf2)
    
    save = None
    savebuf = None
    
    idx = SelectBestIndex(save1, save2)
    
    if idx == 0:
        save = save1
    elif idx == 1:
        save = save2
    else:
        print("Bad save or something")
        return 1
    
    savebuf = save.data
    
    pcdata = save.GetCopyOfPC()
    chunks = save.GetChunkViewsInOrder()
    
    do_exploit(pcdata, argv[2])
    
    asd = bytearray(chunks[1].data[0x238:0x490])
    do_party_test(asd)
    chunks[1].data[0x238:0x490] = asd
    
    save.SetCopyOfPC(pcdata)
    
    save.Fixup()
    
    with open(argv[3], "wb") as f:
        if idx & 1:
            f.write(Savefile.DATA_EMPTY)
            f.write(savebuf)
        else:
            f.write(savebuf)
            f.write(Savefile.DATA_EMPTY)
        
        f.write(savebuf_rest)
    
    return 0

if __name__ == '__main__':
    main()
