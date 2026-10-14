import time

_progress_start_time = None


def print_progress_bar(current, total, bar_length=40, start_time=None):
    """
    Print a progress bar with ETA that updates on the same lines

    """
    # Init start time
    global _progress_start_time
    if start_time is not None:
        _progress_start_time = start_time
    elif _progress_start_time is None or current == 1:
        _progress_start_time = time.time()

    percent = current * 100 // total
    filled = bar_length * current // total
    bar = "█" * filled + "-" * (bar_length - filled)

    # Calculate ETA
    eta_str = "Calculating..."
    if _progress_start_time and current > 0:
        elapsed = time.time() - _progress_start_time
        if elapsed > 0:
            rate = current / elapsed
            if rate > 0:
                remaining = (total - current) / rate

                # Format time nicely
                if remaining < 60:
                    eta_str = f"{int(remaining)}s"
                elif remaining < 3600:
                    mins = int(remaining // 60)
                    secs = int(remaining % 60)
                    eta_str = f"{mins}m {secs}s"
                else:
                    hours = int(remaining // 3600)
                    mins = int((remaining % 3600) // 60)
                    eta_str = f"{hours}h {mins}m"

    # Print progress bar and ETA
    print(f"\r   Progress: [{bar}] {current}/{total} ({percent}%)", end="")
    print(f"\n   ETA: {eta_str}            ", end="", flush=True)
    print("\033[A", end="", flush=True)

    # Reset on completion
    if current == total:
        _progress_start_time = None
