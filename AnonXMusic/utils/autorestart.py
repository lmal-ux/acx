import os
import psutil
import asyncio

async def check_system_resources():
    total_ram = psutil.virtual_memory().total  # Total RAM in bytes
    if total_ram > 2 * 1024**3:  # Convert 2GB to bytes
        print("Total RAM is more than 2GB. Stopping monitoring.")
        return False  # Signal to stop the loop

    ram_usage = psutil.virtual_memory().percent  # RAM usage in percentage
    cpu_usage = psutil.cpu_percent(interval=None)  # CPU usage in percentage (non-blocking)

    print(f"Total RAM: {total_ram / (1024**3):.2f} GB")
    print(f"RAM Usage: {ram_usage}%")
    print(f"CPU Usage: {cpu_usage}%")

    if ram_usage >= 93 and cpu_usage >= 93:
        print("High resource usage detected. Restarting process...")
        os.system(f'kill {os.getpid()} && bash start')

    return True  # Signal to continue the loop

async def monitor():
    while True:
        should_continue = await check_system_resources()
        if not should_continue:
            break  # Exit the loop if RAM is more than 2GB
        await asyncio.sleep(5)  # Check every 5 seconds
