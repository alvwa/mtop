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

def get_size_str(bytes_val):
    """
    Convert bytes to human-readable format.
    
    Args:
        bytes_val: bytes value as an integer

    Example: 1536 bytes -> "1.5 KB"
             1073741824 -> "1.0 GB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024

    return f"{bytes_val:.1f} PB"