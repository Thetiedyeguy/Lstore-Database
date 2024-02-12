PAGE_PER_RANGE = 16
PAGE_SIZE = 4096
RECORD_SIZE = 8
RECORD_PER_PAGE = PAGE_SIZE / RECORD_SIZE
RECORD_PER_RANGE = RECORD_PER_PAGE * PAGE_PER_RANGE
METADATA = 4

# RID first bit = base page[0] or tail page[1]
