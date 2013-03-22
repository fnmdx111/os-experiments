#encoding: utf-8

from Queue import PriorityQueue
from misc import get_cmd

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
            if self.time_demand: # 如果time_demand不为0
                self.time_demand -= 1
                self.priority += 1
                print '%s run' % self.proc_name

                if not self.time_demand:
                    self.status = STATUS_FINISHED
                    print '%s finished' % self.proc_name
        else:
            print 'debug', '%s has already finished' % self.proc_name


    def __str__(self):
        return 'process % 5s; % 5s; % 5s' % (self.proc_name, self.time_demand, self.priority)


    def __repr__(self):
        return self.__str__()



class IdleProcess(ProcessControlBlock):
    def __init__(self):
        super(IdleProcess, self).__init__('Idle', 'inf', 65535)


    def run_once(self):
        print 'idle is the ultimate process'



def display_queue(queue):
    print '** queue ** name;     t;     p'
    for _, item in queue.queue: # 忽略queue里每个条目的优先级
        print '--', item



def dispatch_command():
    while True:
        cmd = raw_input('> ')
        if not len(cmd):
            return None, 0

        if cmd[0] == 'h':
            print 'h(elp)      -- print this text'
            print 'c(ontinue)  -- continue simulation', 'type `c\' or `c times\''
            print 'n(ew pcb)   -- make new PCB and push it into queue',\
                                    'type `n\' or `n name time priority\''
            print 'd(isplay)   -- display the content of queue'
            return 'h', 0
        elif cmd[0] == 'c':
            args = get_cmd(cmd, '%c &i')
            if not args:
                return 'c', -1

            (times,) = args
            if times:
                return 'c', times[0]
            else:
                return 'c', 0
        elif cmd[0] == 'n':
            args = get_cmd(cmd, '%c %s %i %i', hint='proc_n t prior')
            if not args:
                return 'n', -1

            pcb = ProcessControlBlock(*args)
            queue.put((pcb.priority, pcb)) # 优先队列的使用方法是放入队伍时，
                                           # 放入(p, i)，
                                           # 其中p表示优先级，i表示放入的元素
            return 'n', 0
        elif cmd in commands:
            return cmd, commands[cmd]()
        else:
            print 'unrecognized command, type `h\' for help'
            return 'u', -1



if __name__ == '__main__':
    queue = PriorityQueue()
    queue.put((65535, IdleProcess()))

    commands = {'d': lambda: display_queue(queue)}

    cmd_skip_cnt = 0
    while not queue.empty():
        if cmd_skip_cnt:
            cmd_skip_cnt -= 1
        else:
            signal, arg = dispatch_command()
            if signal == 'c':
                cmd_skip_cnt = arg
            else:
                continue

        _, pcb = queue.get() # 忽略queue里存放的优先级

        pcb.run_once()
        if not pcb.is_finished():
            queue.put((pcb.priority, pcb))
            print 'putting %s back into queue' % pcb.proc_name

        display_queue(queue)



