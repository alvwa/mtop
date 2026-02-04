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


def render_cpu_section(stdscr, y, x, width, height, cpu_info):
    """Display CPU information"""
    # stdscr.addstr(row, 0, "CPU USAGE:")
    # row += 1

    # stdscr.addstr(row, 0, f"   Overall: {utils.draw_bar(cpu_info['overall'])}")
    # row += 1

    # stdscr.addstr(row, 0, f"   Cores: {cpu_info['count']}")
    # row += 1

    # stdscr.addstr(row, 0, f"   Per-Core Usage:")
    # row += 1

    # for i, usage in enumerate(cpu_info['per_cpu']):
    #     stdscr.addstr(row, 0, f"   Core {i}: {utils.draw_bar(usage, width=30)}")
    #     row += 1

    # return row + 1
    cpu_win = utils.create_box(stdscr, height, width, y, x, "CPU Usage")
    row = 1

    cpu_win.addstr(row, 2, f"Overall: {utils.draw_bar(cpu_info['overall'], width=width-20)}")
    row += 1

    cpu_win.addstr(row, 2, f"Cores: {cpu_info['count']}")
    row += 2

    available_rows = height - row - 1  # -1 for bottom border
    cores_to_show = min(len(cpu_info['per_cpu']), available_rows)
    
    for i in range(cores_to_show):
        usage = cpu_info['per_cpu'][i]
        cpu_win.addstr(row, 2, f"Core {i}: {utils.draw_bar(usage, width=width-15)}")
        row += 1
    
    # Refresh this window
    cpu_win.refresh()


def render_memory_section(stdscr, y, x, width, height, mem_info):
    """Render memory information in a bordered box."""
    # Create the box
    mem_win = utils.create_box(stdscr, height, width, y, x, "Memory")
    
    row = 1
    
    # RAM
    mem_win.addstr(row, 2, "RAM:")
    row += 1
    
    bar_width = width - 12  # Leave room for label and borders
    mem_win.addstr(row, 2, f"  {utils.draw_bar(mem_info['percent'], width=bar_width)}")
    row += 1
    
    # Size info
    used_str = utils.get_size_str(mem_info['used'])
    total_str = utils.get_size_str(mem_info['total'])
    avail_str = utils.get_size_str(mem_info['available'])
    mem_win.addstr(row, 2, f"  {used_str} / {total_str}")
    row += 1
    mem_win.addstr(row, 2, f"  {avail_str} available")
    row += 2
    
    # Swap (if exists)
    if mem_info['swap_total'] > 0:
        mem_win.addstr(row, 2, "Swap:")
        row += 1
        
        mem_win.addstr(row, 2, f"  {utils.draw_bar(mem_info['swap_percent'], width=bar_width)}")
        row += 1
        
        swap_used_str = utils.get_size_str(mem_info['swap_used'])
        swap_total_str = utils.get_size_str(mem_info['swap_total'])
        mem_win.addstr(row, 2, f"  {swap_used_str} / {swap_total_str}")
    
    mem_win.refresh()

def render_disk_section(stdscr, y, x, width, height, disk_info):
    """Render disk information in a bordered box."""
    disk_win = utils.create_box(stdscr, height, width, y, x, "Disk (/)")
    
    row = 1
    bar_width = width - 12
    
    disk_win.addstr(row, 2, f"{utils.draw_bar(disk_info['percent'], width=bar_width)}")
    row += 2
    
    used_str = utils.get_size_str(disk_info['used'])
    total_str = utils.get_size_str(disk_info['total'])
    free_str = utils.get_size_str(disk_info['free'])
    
    disk_win.addstr(row, 2, f"Used: {used_str} / {total_str}")
    row += 1
    disk_win.addstr(row, 2, f"Free: {free_str}")
    row += 1
    disk_win.addstr(row, 2, f"Usage: {disk_info['percent']:.1f}%")
    
    disk_win.refresh()

def render_network_section(stdscr, y, x, width, height, net_info):
    """Render network information in a bordered box."""
    net_win = utils.create_box(stdscr, height, width, y, x, "Network")
    
    row = 1
    
    # Total transferred
    sent_str = utils.get_size_str(net_info['bytes_sent'])
    recv_str = utils.get_size_str(net_info['bytes_recv'])
    
    net_win.addstr(row, 2, f"Sent: {sent_str} ({net_info['packets_sent']:,} packets)")
    row += 1
    
    net_win.addstr(row, 2, f"Recv: {recv_str} ({net_info['packets_recv']:,} packets)")
    row += 2
    
    # Current rates
    send_rate_str = utils.get_size_str(net_info['send_rate'])
    recv_rate_str = utils.get_size_str(net_info['recv_rate'])
    
    net_win.addstr(row, 2, f"↑ Upload:   {send_rate_str}/s")
    row += 1
    
    net_win.addstr(row, 2, f"↓ Download: {recv_rate_str}/s")
    
    net_win.refresh()



def render_footer(stdscr, row):
    stdscr.addstr(row, 0, "Press 'q' to quit")
    return row + 1


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)
    
    # Initialize network monitor
    net_monitor = NetworkMonitor()
    
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        
        # Get terminal size
        term_height, term_width = stdscr.getmaxyx()
        
        # Clear screen
        stdscr.clear()
        
        # Gather all data
        cpu_info = get_cpu_info()
        mem_info = get_memory_info()
        disk_info = get_disk_info()
        net_info = net_monitor.update()
        
        # Define layout dimensions
        box_height = 12
        box_width = term_width // 2 - 2  # Two columns with spacing
        
        # Top row - CPU (left) and Memory (right)
        render_cpu_section(stdscr, 0, 0, box_width, box_height, cpu_info)
        render_memory_section(stdscr, 0, box_width + 2, box_width, box_height, mem_info)
        
        # Second row - Disk (left) and Battery (right)
        render_disk_section(stdscr, box_height, 0, box_width, 8, disk_info)
        
        # Third row - Network (full width)
        render_network_section(stdscr, box_height + 8, 0, term_width - 1, 8, net_info)
        
        # Footer
        footer_y = box_height + 16
        stdscr.addstr(footer_y, 0, "Press 'q' to quit")
        
        # Refresh main screen
        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)