#encoding: utf-8

from Queue import PriorityQueue
from misc import regularize_args, identity

STATUS_RUNNING = 1
STATUS_FINISHED = 2

class ProcessControlBlock(object):
    def __init__(self, proc_name, time_demand, priority, status=STATUS_RUNNING):
        self.proc_name = proc_name
        self.time_demand = time_demand
        self.priority = priority
        self.status = status


    def is_finished(self):
        return self.status == STATUS_FINISHED


    def run_once(self):
        if not self.is_finished():
            if self.time_demand:
                self.time_demand -= 1
                self.priority += 1
                print '%s run' % self.proc_name

                if not self.time_demand:
                    self.status = STATUS_FINISHED
                    print '%s finished' % self.proc_name
        else:
            print 'debug', '%s has already finished' % self.proc_name


    def __str__(self):
        return 'process %s; %s; %s' % (self.proc_name, self.time_demand, self.priority)


    def __repr__(self):
        return self.__str__()


    @staticmethod
    def make_pcb():
        try:
            proc_name, time_demand, priority = raw_input('proc_n t prior> ').split(' ')
            return ProcessControlBlock(proc_name,
                                       int(time_demand),
                                       int(priority))
        except BaseException:
            print 'aborted'



class IdleProcess(ProcessControlBlock):
    def __init__(self):
        super(IdleProcess, self).__init__('Idle', 'inf', 65535)


    def run_once(self):
        print 'idle is the ultimate process'



def display_queue(queue):
    for item in queue.queue:
        print '--', item



def dispatch_command():
    while True:
        cmd = raw_input('> ')
        if cmd[0] == 'h':
            print 'h(elp)      -- print this text'
            print 'c(ontinue)  -- continue simulation'
            print '\ttype `c\' or `c times\''
            print 'n(ew pcb)   -- make new PCB and push it into queue'
            print '\ttype `n\' or `n name time priority\''
            print 'd(isplay)   -- display the content of queue'
            return 'h', 0
        elif cmd[0] == 'c':
            if cmd == 'c':
                return 'c', 0
            else:
                try:
                    (times,) = regularize_args(None, lambda i: int(i) - 1)(cmd.split())
                    return 'c', times
                except BaseException:
                    print 'incorrect arguments, type h for further help'
                    return 'c', -1
        elif cmd[0] == 'n':
            if cmd == 'n':
                pcb = ProcessControlBlock.make_pcb()
                if pcb:
                    queue.put((pcb.priority, pcb))
                    return 'n', 0
            else:
                try:
                    n, t, p = regularize_args(None, identity, int, int)(cmd.split())
                    pcb = ProcessControlBlock(n, t, p)
                    queue.put((pcb.priority, pcb))
                    return 'n', 0
                except BaseException:
                    print 'incorrect arguments, input proc_name time_demand priority separated by space'
                    return 'n', -1
        elif cmd in commands:
            return cmd, commands[cmd]()
        else:
            print 'unrecognized command, type `h\' for help'
            return 'u', -1



if __name__ == '__main__':
    queue = PriorityQueue()
    l = map(ProcessControlBlock,
            ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
            [2, 3, 1, 4, 3, 1, 2],
            [2, 7, 1, 6, 5, 3, 2])
    queue.put((65535, IdleProcess()))
    for pcb in l:
        queue.put((pcb.priority, pcb))

    commands = {'d': lambda: display_queue(queue)}

    cmd_skip_cnt = 0
    while not queue.empty():
        if cmd_skip_cnt:
            cmd_skip_cnt -= 1
        else:
            signal, arg = dispatch_command()
            if signal == 'c':
                cmd_skip_cnt = arg

        _, pcb = queue.get()

        pcb.run_once()
        if not pcb.is_finished():
            queue.put((pcb.priority, pcb))
            print 'putting %s back into queue' % pcb.proc_name

        display_queue(queue)



