# encoding: utf-8

from collections import defaultdict
from misc import take, get_cmd


class PageTable(object):
    def __init__(self):
        self._l = []


    def register(self, blocks):
        for page, block in enumerate(self._l): # self._l中元素的索引号作为页号，
                                               # 元素作为对应的块号
            if blocks: # 如果还剩下未登记的块，才继续
                if block == 'n/a':
                    self._l[page] = blocks.pop(0)
        self._l.extend(blocks)


    def release(self, *pages):
        for page in pages:
            if len(self._l) > page: # 检测页表长度
                if self._l[page] != 'n/a':
                    print 'releasing page %s' % page
                    self._l[page] = 'n/a'
                else: # 该页已被释放，操作无效
                    print 'trying to release invalid page, aborting'
                    return
            else:
                print 'trying to release invalid page, aborting'
                return
        return True


    def get_block(self, page):
        if page < len(self._l):
            return self._l[page]
        else:
            print 'accessing invalid page %s' % page


    def display(self):
        for pairs in map(lambda *_: _, *take(list(enumerate(self._l)), by=5)): # 按5列表示
            for pair in pairs:
                if pair:
                    # if block != 'n/a':
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
            print 'requested size exceeded available memory'
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
            print 'releasing block %s' % block_number
            self.bit_map[block_number] = 0
            self.available_block_amount += 1





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
            pages = [i for i, content in enumerate(page_tables[proc_name]._l)
                     if content != 'n/a']
        blocks = filter(lambda b: b is not None and b != 'n/a',
                        [page_tables[proc_name].get_block(p) for p in pages])

        memory.release(*blocks)
        page_tables[proc_name].release(*pages)
    elif cmd[0] == 'b':
        print 'available blocks: %s' % memory.available_block_amount
        for line in take(memory.bit_map, by=8):
            print line
    else:
        print 'unrecognized command, type `h\' for help'



if __name__ == '__main__':
    mem, page_tables = Memory(), defaultdict(PageTable)

    while True:
        dispatch_command(mem, page_tables)


