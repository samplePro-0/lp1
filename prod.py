import threading
import time

BUFFER_SIZE = 5
buffer = [None] * BUFFER_SIZE
in_pos = 0
out_pos = 0

# -------- SEMAPHORES --------
empty = threading.Semaphore(BUFFER_SIZE)  # empty slots
full = threading.Semaphore(0)             # filled slots
mutex = threading.Lock()                  # binary lock (mutex)

def producer():
    global buffer, in_pos

    for item in range(1, 11):

        empty.acquire()   # wait for empty slot
        mutex.acquire()   # enter critical section

        buffer[in_pos] = item
        print(f"Producer produced: {item}")
        in_pos = (in_pos + 1) % BUFFER_SIZE

        mutex.release()   # exit critical section
        full.release()    # increase filled slots

        time.sleep(1)


def consumer():
    global buffer, out_pos

    for _ in range(10):

        full.acquire()    # wait for filled slot
        mutex.acquire()   # enter critical section

        item = buffer[out_pos]
        print(f"  Consumer consumed: {item}")
        out_pos = (out_pos + 1) % BUFFER_SIZE

        mutex.release()   # exit critical section
        empty.release()   # increase empty slots

        time.sleep(1)


# -------- MAIN --------
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()
