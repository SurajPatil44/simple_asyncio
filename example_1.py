'''
1. call a function, if result not ready yield
2. manage a schedule loop, and keep calling function
    a. will use round robin for time being
    b. preemptive ??
'''
import time

class task_state:
    pass

class pending(task_state):
    pass

class ready(task_state):
    def __init__(self,name):
        self.name = name
        self.result = None
    def add_result(self,res):
        self.result = res
    def __repr__(self):
        return f"{self.name} task is ready with {self.result}"


#TODO : create a task class to manage context switching, class should hold the information

def wait_for(val,name):
    start = time.time()
    task_rd = False
    discard = yield pending()
    #print(f"task {name} primed")
    Ready = ready(name)
    while True:
        if time.time() - start >= val:
            task_rd = True
            Ready.add_result(task_rd)
            print(f"{name} is ready with {task_rd}")
            break
        elif not task_rd:
            ''' we could return wait time with pending maybe'''
            #print(f"task {name} polled")
            discard = yield pending()
    yield Ready

class scheduler:
    def __init__(self):
        self.ready = []
        self.pend = []
        self.cursor = 0

    def add(self,task):
        '''task is coroutine'''
        ## will prime the task here
        discard = next(task) 
        self.pend.append(task)

    def spin(self):
        ## TODO : instead of polling implement callback

        while len(self.pend) > 0:
            ret = None
            try:
                task = self.pend[self.cursor]
                # we poll it this way
                ret = task.send(None)
                if isinstance(ret,ready):
                    task.close()
                    self.ready.append((task,ret))
                    self.pend.remove(task)
                    # change cursor to first task if any is available
                    if self.pend:
                        self.cursor = 0
                elif isinstance(ret,pending):
                    ret = task.send(None)
                    self.cursor = (self.cursor + 1) % len(self.pend)
                else:
                    raise ValueError(f"Invalid state {ret}")
            except Exception as e:
                print(f"spin failed with {e} and {ret}")
                raise e

if __name__ == "__main__":
    sched = scheduler()
    task1 = wait_for(2,"first 2 second")
    task2 = wait_for(2,"second 2 second")
    task3 = wait_for(2,"third 2 second")
    sched.add(task1)
    sched.add(task2)
    sched.add(task3)
    try:
        sched.spin()
    except Exception as e:
        print(e)

    for task in sched.ready:
        print(task)
