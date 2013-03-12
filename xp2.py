from collections import defaultdict
from misc import take, get_cmd


class PageTable(object):
    def __init__(self):
        self._l = []


    def register(self, blocks):
        for page, block in enumerate(self._l):
            if blocks:
                if block == 'n/a':
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
            # if block != 'n/a':
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
    cmd = raw_input('> ')
    if cmd[0] == 'h':
        print 'h(elp)             -- print this text'
        print 'a(llocate)         -- request for space allocation'
        print '\ttype `a\' or `a proc_name size\''
        print 'r(elease)          -- release space'
        print '\ttype `r\' or `r proc_name block0 block1 block2 ...\''
        print 'd(isplay)          -- display the content of the page table'
        print 'display (b)it map  -- display the content of the bit map'
    elif cmd[0] == 'd':
        args = get_cmd(cmd, '%c &s')
        if not args:
            return

        (proc_names,) = args
        if not proc_names:
            proc_names = page_tables.keys()

        for name in proc_names:
            print '--', name, '--'
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
            pages = [i for i, content in enumerate(page_tables[proc_name]._l)
                     if content != 'n/a']

        memory.release(*pages)
        page_tables[proc_name].release(*pages)
    elif cmd[0] == 'b':
        print 'available blocks: %s' % memory.available_block_amount
        for line in take(memory.bit_map):
            print line
    else:
        print 'unrecognized command, type `h\' for help'



if __name__ == '__main__':
    mem, page_tables = Memory(), defaultdict(PageTable)

    while True:
        dispatch_command(mem, page_tables)


