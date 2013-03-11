from collections import defaultdict
from misc import take


class PageTable(object):
    def __init__(self):
        self._l = []


    def register(self, blocks):
        for page, block in enumerate(self._l):
            if blocks:
                if block < 0:
                    self._l[page] = blocks[0]
                    blocks = blocks[1:]
        self._l.extend(blocks)


    def release(self, *pages):
        for page in pages:
            if len(self._l) > page:
                if self._l[page] != 'n/a':
                    print 'releasing page %s' % page
                    self._l[page] = 'n/a'
                else:
                    print 'trying to release invalid page, aborting'
                    return
            else:
                print 'trying to release invalid page, aborting'
                return


    def display(self):
        for page, block in enumerate(self._l):
            if block != 'n/a':
                print '% 4s | % 4s' % (page, block)


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
            print 'requested size exceeded available memory'
            return

        allocated = []
        for block_number, block_not_available in enumerate(self.bit_map):
            if not block_not_available:
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





def dispatch_command(memory, page_tables):
    cmd = raw_input('> ').split()
    if cmd[0] == 'h':
        print 'h(elp)             -- print this text'
        print 'a(llocate)         -- request for space allocation'
        print '\ttype `a\' or `a proc_name size\''
        print 'r(elease)          -- release space'
        print '\ttype `r\' or `r proc_name block0 block1 block2 ...\''
        print 'd(isplay)          -- display the content of the page table'
        print 'display (b)it map  -- display the content of the bit map'
    elif cmd[0] == 'd':
        if len(cmd) == 1:
            for name in page_tables:
                print '--', name, '--'
                page_tables[name].display()
        else:
            _, name = cmd
            page_tables[name].display()
    elif cmd[0] == 'a':
        if len(cmd) == 1:
            proc_name, size = raw_input('proc_name size> ').split()
        else:
            _, proc_name, size = cmd

        try:
            size = int(size)
        except BaseException:
            print 'incorrect argument, input number only'
            return

        cmd_allocation(memory, page_tables, proc_name, size)
    elif cmd[0] == 'r':
        if len(cmd) == 1:
            _ = raw_input('proc_name pages> ').split()
            try:
                proc_name, pages = _[0], _[1:]
            except BaseException:
                print 'incorrect argument'
                return
        else:
            proc_name = cmd[1]
            pages = cmd[2:]

        try:
            pages = map(int, pages)
        except BaseException:
            print 'incorrect argument, input number only'
            return

        cmd_release(memory, page_tables, proc_name, pages)
    elif cmd[0] == 'b':
        print 'available blocks: %s' % memory.available_block_amount
        for line in take(memory.bit_map):
            print line
    else:
        print 'unrecognized command, type `h\' for help'


def cmd_release(m, pts, proc_name, pages):
    m.release(*pages)
    pts[proc_name].release(*pages)


def cmd_allocation(m, pts, proc_name, size):
    blocks = m.allocate(size)

    print '%s allocated' % blocks

    if blocks:
        pts[proc_name].register(blocks)


if __name__ == '__main__':
    mem, page_tables = Memory(), defaultdict(PageTable)

    while True:
        dispatch_command(mem, page_tables)


