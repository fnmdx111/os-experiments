# encoding: utf-8

from collections import defaultdict
from misc import take, get_cmd


class PageTable(object):
    def __init__(self, memory):
        self.table = {}
        self.memory = memory


    def register(self, blocks):
        page_numbers = self.table.keys()
        max_page_number = max(self.table.keys()) if self.table.keys() else -1
        unused_page_numbers = set(range(max_page_number)) - set(page_numbers)

        for page_number in unused_page_numbers: # 先把未用的页号填满
            if blocks:
                self.table[page_number] = blocks.pop(0)
            else: # 没有要登记的块了，可以直接返回了
                return

        page_number = max_page_number + 1 # 未用块号全部填满之后
                                          # 从最大块号 + 1开始继续登记
        for block in blocks:
            self.table[page_number] = block
            page_number += 1


    def release(self, *pages):
        if len(pages) > len(self.table):
            print 'requested page amount exceeds page table length, aborting'
            return

        for page in pages:
            if page in self.table:
                self.memory.release(self.get_block(page))

                print 'releasing page %s' % page
                del self.table[page]
            else:
                print 'trying to release invalid page %s, aborting' % page
                return


    def get_block(self, page):
        if page in self.table:
            return self.table[page]
        else:
            print 'accessing invalid page %s' % page


    def display(self):
        if not self.table:
            print 'empty'
            return
        for pairs in map(lambda *_: _, *take(list(self.table.iteritems()), by=5)): # 按5列表示
            for pair in pairs:
                if pair:
                    print '%s | %s' % (str(pair[0]).rjust(3), str(pair[1]).ljust(3)),
            print


class Memory(object):
    def __init__(self, size=256):
        self.size = size
        self.total_block_amount = 64
        self.available_block_amount = self.total_block_amount
        self.page_size = self.size / self.total_block_amount

        self.bit_map = map(lambda _: 0, range(self.total_block_amount))


    def allocate(self, size):
        blocks_needed = size / self.page_size + (1 if size % self.page_size else 0)
        print '%s blocks needed, %s available, after allocation %s available' % (blocks_needed, self.available_block_amount, self.available_block_amount - blocks_needed)

        if blocks_needed > self.available_block_amount:
            print 'requested size exceeded available memory size'
            return

        allocated = []
        for block_number, block_not_available in enumerate(self.bit_map):
            if not block_not_available: # 即该块可用
                if len(allocated) < blocks_needed:
                    allocated.append(block_number)
                    self.bit_map[block_number] = 1
                    self.available_block_amount -= 1
                else:
                    break

        return allocated


    def release(self, *block_numbers):
        for block_number in block_numbers:
            self.bit_map[block_number] = 0
            self.available_block_amount += 1
            print 'releasing block %s' % block_number





def dispatch_command(memory, page_tables):
    cmd = raw_input('> ')
    if cmd[0] == 'h':
        print 'h(elp)             -- print this text'
        print 'a(llocate)         -- request for space allocation', 'type `a\' or `a proc_name size\''
        print 'r(elease)          -- release space', 'type `r\' or `r proc_name block0 block1 block2 ...\''
        print 'd(isplay)          -- display the content of the page table'
        print 'display (b)it map  -- display the content of the bit map'
    elif cmd[0] == 'd':
        args = get_cmd(cmd, '%c &s')
        if not args:
            return

        (proc_names,) = args
        if not proc_names:
            proc_names = sorted(page_tables.keys())

        for name in proc_names:
            if name not in page_tables:
                print '%s is not a process' % name
            else:
                print '--', name, '--', ' page | block'
                page_tables[name].display()
    elif cmd[0] == 'a':
        args = get_cmd(cmd, '%c %s %i', hint='proc_name size')
        if not args:
            return
        proc_name, size = args

        blocks = memory.allocate(size)
        print '%s allocated' % blocks
        if blocks:
            page_tables[proc_name].register(blocks)
    elif cmd[0] == 'r':
        args = get_cmd(cmd, '%c %s &i', hint='proc_name pages')
        if not args:
            return
        proc_name, pages = args
        if not pages:
            pages = page_tables[proc_name].table.keys()

        page_tables[proc_name].release(*pages)
    elif cmd[0] == 'b':
        print 'available blocks: %s' % memory.available_block_amount
        for line in take(memory.bit_map, by=8):
            print line
    else:
        print 'unrecognized command, type `h\' for help'



if __name__ == '__main__':
    mem = Memory()
    page_tables = defaultdict(lambda: PageTable(mem))

    while True:
        dispatch_command(mem, page_tables)


