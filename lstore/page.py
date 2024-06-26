from lstore.config import *

class Page:

    def __init__(self):
        self.num_records = 0
        self.data = bytearray(4096)
        self.tps = 0
        self.dirty = True

    def has_capacity(self):
        return self.num_records < RECORD_PER_PAGE

    def write(self, value, location = - 1):
        if location == -1:
            location = self.num_records
            if self.has_capacity():
                self.data[location * 8:(location + 1) * 8] = int(value).to_bytes(8, byteorder = 'big')
                self.num_records += 1
                self.dirty = True
            else:
                raise Exception("Page is full")
        else:
            self.data[location * 8:(location + 1) * 8] = int(value).to_bytes(8, byteorder = 'big')
            self.dirty = True
        pass

    def get_value(self, location):
        return int.from_bytes(self.data[location * 8:(location + 1) * 8], "big")

class PageRange:
    def __init__(self, num_columns, num_base_pages = 16):
        self.num_columns = num_columns
        self.num_base_pages = num_base_pages
        self.base_pages = [[None for i in range(self.num_columns)] for _ in range(num_base_pages)] # 16 base pages with a physical page for each row
        self.tail_pages = []  # Start with a single tail page
        self.base_dirty = [False for i in range (self.num_base_pages)]
        self.tail_dirty = []
        self.current_base_idx = 0
        self.current_tail_idx = 0
        self.dirty = True
        self.next = None
        self.prev = None
        self.idx = None
        self.pinned = 0


    def make_tail_page(self):
        self.tail_pages.append([Page() for _ in range(self.num_columns)])
        self.current_tail_idx += 1
        self.dirty = True

    def make_base_page(self, idx):
        self.base_pages[idx] = [Page() for _ in range(self.num_columns)]
        self.current_base_idx += 1
        self.dirty = True

    def get_current_base(self, column):
        if(self.current_base_idx != 0):
            if self.base_pages[self.current_base_idx - 1][column].has_capacity():
                return self.base_pages[self.current_base_idx - 1][column]
            else:
                self.make_base_page(self.current_base_idx)
                return self.base_pages[self.current_base_idx - 1][column]
        else:
            #raise Exception("No base pages here")
            self.make_base_page(self.current_base_idx)
            return self.base_pages[self.current_base_idx - 1][column]

    def get_current_tail(self, column):
        if(self.current_tail_idx != 0):
            if self.tail_pages[self.current_tail_idx - 1][column].has_capacity():
                return self.tail_pages[self.current_tail_idx - 1][column]
            else:
                self.make_tail_page()
                return self.tail_pages[self.current_tail_idx - 1][column]
        else:
            self.make_tail_page()
            return self.tail_pages[self.current_tail_idx - 1][column]
            #raise Exception("No tail pages here")
