import psutil
import time
import utils
import curses

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


def get_memory_info():
    """Gather memory usage information"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        'total': mem.total,
        'used': mem.used,
        'available': mem.available,
        'percent': mem.percent,
        'swap_total': swap.total,
        'swap_used': swap.used,
        'swap_percent': swap.percent
    }


def render_header(stdscr, row):
    stdscr.addstr(row, 0, "=== SYSTEM MONITOR ===")
    return row + 2


def render_cpu_section(stdscr, row, cpu_info):
    """Display CPU information"""
    stdscr.addstr(row, 0, "CPU USAGE:")
    row += 1

    stdscr.addstr(row, 0, f"   Overall: {utils.draw_bar(cpu_info['overall'])}")
    row += 1

    stdscr.addstr(row, 0, f"   Cores: {cpu_info['count']}")
    row += 1

    stdscr.addstr(row, 0, f"   Per-Core Usage:")
    row += 1

    for i, usage in enumerate(cpu_info['per_cpu']):
        stdscr.addstr(row, 0, f"   Core {i}: {utils.draw_bar(usage, width=30)}")
        row += 1

    return row + 1


def render_memory_section(stdscr, row, mem_info):
    """Display memory information"""
    stdscr.addstr(row, 0, "Memory:")
    row += 1

    stdscr.addstr(row, 0, f"   RAM: {utils.draw_bar(mem_info['percent'])}")
    row += 1

    used_str = utils.get_size_str(mem_info['used'])
    total_str = utils.get_size_str(mem_info['total'])
    available_str = utils.get_size_str(mem_info['available'])
    stdscr.addstr(row, 0, f"      {used_str} / {total_str} ({available_str} available)")
    row += 1

    if mem_info['swap_total'] > 0:
        stdscr.addstr(row, 0, f"   Swap: {utils.draw_bar(mem_info['swap_percent'])}")
        row += 1

        swap_used = utils.get_size_str(mem_info['swap_used'])
        swap_total = utils.get_size_str(mem_info['swap_total'])
        stdscr.addstr(row, 0, f"      {swap_used} / {swap_total}")
        row += 1
    
    return row + 1


def render_footer(stdscr, row):
    stdscr.addstr(row, 0, "Press 'q' to quit")
    return row + 1


def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Don't block on input
    stdscr.timeout(1000)    # Refresh every 1000ms

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break

        stdscr.clear()

        # Gather all data
        cpu_info = get_cpu_info()
        mem_info = get_memory_info()

        # Render data
        row = 0
        row = render_header(stdscr, row)
        row = render_cpu_section(stdscr, row, cpu_info)
        row = render_memory_section(stdscr, row, mem_info)
        row = render_footer(stdscr, row)

        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)