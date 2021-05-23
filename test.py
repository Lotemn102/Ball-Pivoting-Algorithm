import threading
import time

def foo():
    print("sleeping")
    time.sleep(5)
    print("done sleeping")

if __name__ == "__main__":
    t1 = threading.Thread(target=foo)

    print("before")
    t1.start()
    print("after")
