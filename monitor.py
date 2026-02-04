import psutil
import time
import utils
import curses

class NetworkMonitor:
    """Track network statistics over time."""

    def __init__(self):
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = time.time()
        self.send_rate = 0
        self.recv_rate = 0

    def update(self):
        """Update network stats and calculate rates."""
        net_io = psutil.net_io_counters()
        current_time = time.time()

        time_delta = current_time - self.last_time

        if time_delta > 0:
            self.send_rate = (net_io.bytes_sent - self.last_bytes_sent) / time_delta
            self.recv_rate = (net_io.bytes_recv - self.last_bytes_recv) / time_delta
        
        self.last_bytes_sent = net_io.bytes_sent
        self.last_bytes_recv = net_io.bytes_recv
        self.last_time = current_time

        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'send_rate': self.send_rate,    # Bytes per second
            'recv_rate': self.recv_rate     # Bytes per second
        }


def get_cpu_info():
    """Gather all CPU information."""
    # Get CPU usage (wait 0.1 seconds for accurate reading)
    cpu_percent = psutil.cpu_percent(interval=1.0)
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

def get_disk_info():
    """Gather disk usage information."""
    disk = psutil.disk_usage('/')

    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }


def render_header(stdscr, row):
    try:
        stdscr.addstr(row, 0, "=== SYSTEM MONITOR ===")
    except curses.error:
        pass
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

def render_disk_section(stdscr, row, disk_info):
    """Display disk information"""
    stdscr.addstr(row, 0, "Disk (/):")
    row += 1

    stdscr.addstr(row, 0, f"   {utils.draw_bar(disk_info['percent'])}")
    row += 1

    used_str = utils.get_size_str(disk_info['used'])
    total_str = utils.get_size_str(disk_info['total'])
    free_str = utils.get_size_str(disk_info['free'])
    stdscr.addstr(row, 0, f"      {used_str} / {total_str} ({free_str} free)")
    row += 1

    return row + 1

def render_network_section(stdscr, row, net_info):
    """Display network statistics."""
    stdscr.addstr(row, 0, "Network:")
    row += 1
    
    # Total transferred
    sent_str = utils.get_size_str(net_info['bytes_sent'])
    recv_str = utils.get_size_str(net_info['bytes_recv'])
    
    stdscr.addstr(row, 0, f"   Sent: {sent_str} ({net_info['packets_sent']:,} packets)")
    row += 1
    
    stdscr.addstr(row, 0, f"   Recv: {recv_str} ({net_info['packets_recv']:,} packets)")
    row += 1
    
    # Current rates (if available)
    if 'send_rate' in net_info and 'recv_rate' in net_info:
        send_rate_str = utils.get_size_str(net_info['send_rate'])
        recv_rate_str = utils.get_size_str(net_info['recv_rate'])
        
        stdscr.addstr(row, 0, f"   Upload speed: {send_rate_str}/s")
        row += 1
        
        stdscr.addstr(row, 0, f"   Download speed: {recv_rate_str}/s")
        row += 1
    
    return row + 1



def render_footer(stdscr, row):
    stdscr.addstr(row, 0, "Press 'q' to quit")
    return row + 1


def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Don't block on input
    stdscr.timeout(1000)    # Refresh every 1000ms

    net_monitor = NetworkMonitor()

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break

        stdscr.clear()
        max_row = stdscr.getmaxyx()[0] - 1  # Get terminal height

        # Gather all data
        cpu_info = get_cpu_info()
        mem_info = get_memory_info()
        disk_info = get_disk_info()
        net_info = net_monitor.update()

        # Render data (stop if exceeds terminal height)
        row = 0
        if row < max_row:
            row = render_header(stdscr, row)
        if row < max_row:
            row = render_cpu_section(stdscr, row, cpu_info)
        if row < max_row:
            row = render_memory_section(stdscr, row, mem_info)
        if row < max_row:
            row = render_disk_section(stdscr, row, disk_info)
        if row < max_row:
            row = render_network_section(stdscr, row, net_info)
        if row < max_row:
            row = render_footer(stdscr, row)

        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)