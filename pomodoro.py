import select
import sys
import time


def timeout_input(minutes, prompt=""):
    seconds = minutes*60
    sys.stdout.write("{}\n".format(prompt))
    for t in range(seconds,0,-1):
        m, s = divmod(t, 60)
        h, m = divmod(m, 60)
        sys.stdout.write("\x1b[2K\r {:02d}:{:02d}:{:02d}".format(h,m,s))
        sys.stdout.flush()
        ready, _, _ = select.select([sys.stdin], [], [], 1)
    if ready:
        return True
    else:
        sys.stdout.write('\n')
        sys.stdout.flush()
        return False


def mini_countdown(seconds):
    for t in range(seconds, -1, -1):
        time.sleep(1)
        print("Starting in " + str(t), end="\r")
    print()
