
from libpoke_types.poke import *
from libpoke_types.savefile import NUM_SECTORS_PER_SLOT, SECTOR_SIZE, SaveChunk


class Savefile:
    DATA_SIZE = SECTOR_SIZE * NUM_SECTORS_PER_SLOT
    DATA_EMPTY = b'\xFF' * DATA_SIZE
    PC_BUFFER_COUNT = 420
    PC_BUFFER_ENTRY_SIZE = 80
    PC_BUFFER_SIZE = PC_BUFFER_ENTRY_SIZE * PC_BUFFER_COUNT
    PC_SCREEN_ROWS = 6
    PC_SCREEN_COLUMNS = 5
    PC_SCREEN_SLOTS_COUNT = PC_SCREEN_ROWS * PC_SCREEN_COLUMNS
    PC_SCREEN_FULL_BYTES = PC_BUFFER_ENTRY_SIZE * PC_SCREEN_SLOTS_COUNT
    
    def __init__(self, buf):
        self.data = bytearray(buf)
        self.view = memoryview(self.data)
    
    def GetChunkView(self, raw_index: int) -> SaveChunk:
        offs = SECTOR_SIZE * raw_index
        view = self.view[offs:offs+SECTOR_SIZE]
        return SaveChunk.from_buffer(view)
    
    def GetChunkViewsInOrder(self) -> "list[SaveChunk]":
        views = [None] * NUM_SECTORS_PER_SLOT
        
        for i in range(len(views)):
            view = self.GetChunkView(i)
            views[view.ID] = view
        
        return views
    
    def GetCopyOfPC(self):
        res = bytearray(self.PC_BUFFER_SIZE)
        offs = 0
        chunks = self.GetChunkViewsInOrder()
        
        for i in range(5, 14):
            chunk = chunks[i]
            len = chunk.GetLength()
            
            len = min(len, self.PC_BUFFER_SIZE - offs)
            
            if i == 5:
                len -= 4
                res[offs:offs+len] = chunk.data[4:len+4]
            else:
                res[offs:offs+len] = chunk.data[0:len]
            
            offs += len
        
        assert offs == self.PC_BUFFER_SIZE, "bruh 1"
        
        return res
    
    def SetCopyOfPC(self, buf):
        offs = 0
        chunks = self.GetChunkViewsInOrder()
        
        for i in range(5, 14):
            chunk = chunks[i]
            len = chunk.GetLength()
            
            len = min(len, self.PC_BUFFER_SIZE - offs)
            
            if i == 5:
                len -= 4
                chunk.data[4:len+4] = buf[offs:offs+len]
            else:
                chunk.data[0:len] = buf[offs:offs+len]
            
            offs += len
        
        assert offs == self.PC_BUFFER_SIZE, "bruh 2"
    
    def GetValidationError(self):
        view = self.GetChunkView(0)
        err = view.GetError()
        if err:
            return err
        
        n_index = view.save_index
        n_chunk = view.ID
        
        for i in range(NUM_SECTORS_PER_SLOT):
            view = self.GetChunkView(i)
            
            if view.save_index != n_index:
                return 3
            if view.ID != n_chunk:
                return 4
            
            n_chunk += 1
            if n_chunk == NUM_SECTORS_PER_SLOT:
                n_chunk = 0
        
        return 0
    
    def Fixup(self):
        for i in range(NUM_SECTORS_PER_SLOT):
            view = self.GetChunkView(i)
            view.Regenerate()
    
    
def SelectBestIndex(arg1: Savefile, arg2: Savefile):
    nbest = None
    n_idx = 0
    
    if not arg1.GetValidationError():
        n_id = arg1.GetChunkView(0).save_index
        if n_id >= n_idx:
            n_idx = n_id
            nbest = 0
    
    if not arg2.GetValidationError():
        n_id = arg2.GetChunkView(0).save_index
        if n_id >= n_idx:
            n_idx = n_id
            nbest = 1
    
    return nbest
