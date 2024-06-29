import threading
import time
import os
import sys
import signal
import ctypes

# File to store the remaining time
TICK_TOCK = "remaining_time.txt"
# Duration of the timer (3 hours in seconds)
TIMER_DURATION = 10800


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def admin_perm():
    if not is_admin():
        # Re-run the script with admin privileges
        try:
            print("Requesting administrative privileges...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)  # Exit the current process
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            time.sleep(5)
            sys.exit(1)

def get_system32_path():
    # Get the Windows system directory path
    system32_path = os.path.join(os.environ['WINDIR'], 'System32')
    return system32_path

def load_remaining_time():
    """Load the remaining time from file or return the full duration if file doesn't exist."""
    if os.path.exists(TICK_TOCK):
        with open(TICK_TOCK, "r") as file:
            try:
                remaining_time = int(file.read().strip())
                return remaining_time
            except ValueError:
                return TIMER_DURATION
    return TIMER_DURATION

def save_remaining_time(remaining_time):
    """Save the remaining time to file."""
    with open(TICK_TOCK, "w") as file:
        file.write(str(remaining_time))

def timer_thread():
    """Thread function to handle the timer."""
    remaining_time = load_remaining_time()
    start_time = time.time()

    while remaining_time > 0:
        elapsed = time.time() - start_time
        remaining_time -= elapsed
        save_remaining_time(int(remaining_time))
        if remaining_time <= 0:
            print("\nTime's up! Program will self-destruct.")
            os.remove(TICK_TOCK)
            os.kill(os.getpid(), signal.SIGTERM)
        start_time = time.time()
        time.sleep(1)

def cli_thread():
    """Thread function to handle user CLI interaction."""
    while True:
        print(f"Welcome {os.getlogin()}! \nThis is a trial version after 3 hours the program will self distruct.")
        command = input("Enter a command (type 'exit' to quit): ")
        if command.lower() == 'exit':
            print("Exiting program.")
            sys.exit(0)
        else:
            print(f"You entered: {command}")

def main():
    # async_task = asyncio.create_task(is_admin())
    # asyncio.run(async_task)
    admin_perm()
    cli = threading.Thread(target=cli_thread, daemon=True)
    threading.Thread(target=timer_thread, daemon=True).start()    

    cli.start()
    # Wait for the CLI thread to finish
    cli.join()

if __name__ == "__main__":
    main()
