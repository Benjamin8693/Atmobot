import asyncio
from datetime import datetime
from datetime import timedelta

scheduled_tasks = set()
schedule_tasks_lock = asyncio.Lock()

async def timer_loop():
    while True:
        await asyncio.sleep(1)
        async with schedule_tasks_lock:
            for task in scheduled_tasks:
                if datetime.now() >= task.scheduled_time:
                    if not task.running:
                        task.run()

class ManualEvent:
    def __init__(self, task, *args):
        self.event = asyncio.Event()
        self.task = task
        self.running_task = None
        self.running = False
        self.scheduler = asyncio.create_task(self.__scheduler())
        self.args = args
        
    async def cancel(self):
        self.scheduler.cancel()
    
    def run(self):
        self.event.set()
        
    def run_now(self):
        self.run()
        
    async def reset(self):
        self.event.clear()
    
    async def __scheduler(self):
        while True:
            await self.event.wait()
            self.running = True
            if len(self.args) > 0:
                self.running_task = asyncio.create_task(self.task(*self.args))
            else:
                self.running_task = asyncio.create_task(self.task())
            await self.running_task
            self.running_task = None
            self.running = False
            await self.reset()

class TickEvent(ManualEvent):
    def __init__(self, tick_rate, task, *args, first_run_date = None):
        ManualEvent.__init__(self, task, *args)
        if not "custom_a_scheduler_timer_loop" in globals():
            globals()["custom_a_scheduler_timer_loop"] = asyncio.create_task(timer_loop())
        self.tick_rate = tick_rate
        if first_run_date is None:
            self.scheduled_time = datetime.now() + tick_rate
        else:
            self.scheduled_time = first_run_date
        
    async def create(tick_rate, task, *args):
        output = TickEvent(tick_rate, task, *args)
        async with schedule_tasks_lock:
            scheduled_tasks.add(output)
        return output
    
    async def cancel(self):
        await ManualEvent.cancel(self)
        async with schedule_tasks_lock:
            scheduled_tasks.remove(self)
            
    def run_now(self):
        self.scheduled_time = datetime.now()
    
    async def reset(self):
        self.event.clear()
        self.scheduled_time = datetime.now() + self.tick_rate

class DateEvent(ManualEvent):
    def __init__(self, date, task, *args):
        ManualEvent.__init__(self, task, *args)
        if not "custom_a_scheduler_timer_loop" in globals():
            globals()["custom_a_scheduler_timer_loop"] = asyncio.create_task(timer_loop())
        self.scheduled_time = date
        
    async def create(date, task, *args):
        output = DateEvent(date, task, *args)
        async with schedule_tasks_lock:
            scheduled_tasks.add(output)
        return output
        
    def run_now(self):
        self.scheduled_time = datetime.now()
    
    async def cancel(self):
        await ManualEvent.cancel(self)
        async with schedule_tasks_lock:
            scheduled_tasks.remove(self)
    
    async def reset(self):
        await self.cancel()

#For Testing
async def boop(input):
    print(input)

async def tests():
    # A event which runs after specific date (run_date, task, *task_args)
    a = await DateEvent.create(datetime.now() + timedelta(seconds=3), boop, "a")

    # A event which runs every * (minimum time is 1 second), (tick_rate, task, *task_args, first_run_date = None).
    # You can set first_run_date to a datetime to state when the first run should happen (datetime.now() causes it's first run to run on creation) if first_run_date isn't set then the first run is after the first duration has passed
    b = await TickEvent.create(timedelta(seconds=1), boop, "b")

    # You can use a.run_now() to run a asap and a.cancel() to cancel a otherwise a runs normally
    # A manual event which only runs if run() is ran
    c = ManualEvent(boop, "c")
    await asyncio.sleep(2)
    c.run()

    await asyncio.sleep(2)

asyncio.run(tests())
