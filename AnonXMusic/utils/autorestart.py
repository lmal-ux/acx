import os
import psutil
import asyncio
from datetime import datetime, timedelta
try: from zoneinfo import ZoneInfo; ZI = True  
except: ZI = False  

async def check_system_resources():
    log_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
    log_file = os.path.join(log_dir, "ram.log")
    
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%y:%H:%M:%S") if ZI else (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%d-%m-%y:%H:%M:%S")
    total_ram = psutil.virtual_memory().total  

    if total_ram > 2 * 1024**3:  
        message = f"Total RAM is more than 2GB. Stopping monitoring."
        print(message)
        return False  

    ram_usage = psutil.virtual_memory().percent 
    swap_usage = psutil.swap_memory().percent 
    cpu_usage = psutil.cpu_percent(interval=None)  
    
    message = (
        f"[{timestamp}] Total RAM: {total_ram / (1024**3):.2f} GB\n"
        f"[{timestamp}] RAM Usage: {ram_usage}%\n"
        f"[{timestamp}] Swap Usage: {swap_usage}%\n"
        f"[{timestamp}] CPU Usage: {cpu_usage}%"
    )

    with open(log_file, "a") as log:
        log.write(message + "\n\n\n")

    if (ram_usage >= 93 and cpu_usage >= 93) or ram_usage>=98:
        warning = f"{timestamp} High resource usage detected. Restarting process..."
        print(warning)
        with open(log_file+'s', "a") as log:
            log.write(warning + "\n")
        os.system(f'kill {os.getpid()} && bash start')

    return True  

async def monitor():
    while True:
        try:
         should_continue = await check_system_resources()
        except :
            should_continue=False
        if not should_continue:
            break  
        await asyncio.sleep(5)
