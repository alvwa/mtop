import psutil
import time
import os

def clear_screen():
    os.system('clear')

def draw_bar(percentage, width=40):
    """
    Draw a text-based progress bar

    Args:
        percentage: Value from 0-100
        width: Total characters in the bar
    
    Returns:
        String with the formatted bar
    """
    filled = int(width * percentage / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percentage:5.1f}%"

def get_cpu_info():
    """Gather all CPU information."""
    # Get CPU usage (wait 0.1 seconds for accurate reading)
    cpu_percent = psutil.cpu_percent(interval=0.1)
    per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_count = psutil.cpu_count()

    return {
        'overall': cpu_percent,
        'per_cpu': per_cpu,
        'count': cpu_count
    }

def render_cpu_section(cpu_info):
    """Display CPU information"""
    print("=== CPU USAGE ===")
    print(f"Overall: {draw_bar(cpu_info['overall'])}")
    print(f"Cores: {cpu_info['count']}")
    print(f"\nPer-Core:")
    for i, usage in enumerate(cpu_info['per_cpu']):
        print(f"  Core {i}: {draw_bar(usage, width=30)}")


def main():
    try:
        while True:
            clear_screen()
            render_cpu_section(get_cpu_info())
            print("\nPress Ctrl+C to exit")

            time.sleep(1)
    except KeyboardInterrupt:
        clear_screen()
        print("=== Exiting Terminal Monitoring Dashboard ===")
    
if __name__ == "__main__":
    main()