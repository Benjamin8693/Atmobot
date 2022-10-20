from ast import expr_context
import asyncio
from datetime import date, datetime
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
        if type(self.task) == str:
            self.task = bot.get_scheduled_function(self.task)
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
            try:
                if len(self.args) > 0:
                    self.running_task = asyncio.create_task(self.task(*self.args))
                else:
                    self.running_task = asyncio.create_task(self.task())
                await self.running_task
            except Exception as e:
                print(e)
                await self.cancel()
                return
            await self.running_task
            self.running_task = None
            self.running = False
            await self.reset()

class TickEvent(ManualEvent):
    def __init__(self, first_run_date, tick_rate, task, *args):
        ManualEvent.__init__(self, task, *args)
        if not "custom_a_scheduler_timer_loop" in globals():
            globals()["custom_a_scheduler_timer_loop"] = asyncio.create_task(timer_loop())
        if type(tick_rate) in (int, float):
            tick_rate = timedelta(seconds=tick_rate)
        self.tick_rate = tick_rate
        now = datetime.now()
        if type(first_run_date) in (int, float):
            first_run_date = datetime.fromtimestamp(first_run_date)
        if first_run_date is None:
            self.scheduled_time = now + tick_rate
        # TODO: This helps tick tasks start up shortly after being loaded, so long as their initial time has passed
        # We need to add a new setting to tick tasks where you can toggle this behavior, because sometimes it could screw things up with daily routines
        elif now > first_run_date:
            self.scheduled_time = now + timedelta(seconds = 5)
        else:
            self.scheduled_time = self.next_datetime(first_run_date)

    def next_datetime(self, current) -> datetime:
        hour = current.hour
        minute = current.minute
        second = current.second
        now = datetime.now()
        repl = now.replace(hour=hour, minute=minute, second=second)
        while repl <= now:
            repl = repl + timedelta(days=1)
        return repl
        
    async def create(first_run_date, tick_rate, task, *args):
        output = TickEvent(first_run_date, tick_rate, task, *args)
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
        if type(date) in (int, float):
            date = datetime.fromtimestamp(date)
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
