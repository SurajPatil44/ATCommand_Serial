import threading
import signal
import sys
import serial
import time
from queue import Queue
import queue
from keyboard_input import ProcessCommand

import codecs
codecs.register_error("strict", codecs.ignore_errors)


class PortOpenError(Exception):
    pass


def write_and_wait(ser,cmd_q=None):
    try:
        while True:
            if not ser.is_open:
                break
            cmd = None
            if cmd_q:
                try:
                    cmd = cmd_q.get_nowait()
                except queue.Empty:
                    pass
            else:
                pass
            if cmd:
            #cmd = cmd.encode()
                cmd = cmd + b"\r\n"
                #print(f"{cmd}")
                ser.write(cmd)
                ser.flush()
                time.sleep(0.1)
               #print(f"{ser.in_waiting}")
                #ser.reset_output_buffer()
                ser.cancel_write()
                cmd_q.task_done()
            else:
                pass
            while True:
                if ser.in_waiting:
                    #print(f"{ser.in_waiting}")
                    #print(f"{ser.out_waiting}")
                    #print("here.....")
                    out = ser.read(ser.in_waiting)
                    fileout.write(out)
                    print(out.decode())
                    break
                else:
                    break
    except Exception as E:
        print(f"T1 panicked {E}")
        ser.close()


def signal_hdlr(signum,frame):
    print("getting ctrl + c atleast")
    sys.exit(1)


if __name__ == "__main__":
    fileout = open("out","wb+")
    exit_evt = threading.Event()
    signal.signal(signal.SIGINT,signal_hdlr)
    cmd_q = Queue()
    com = "COM6"
    try:
        PC = ProcessCommand(cmd_q)
        ser = serial.Serial(com,115200,timeout=0)
        T1 = threading.Thread(target=write_and_wait,args=(ser,cmd_q))
        T1.daemon = True
        T1.start()
        PC.run()
        while True:
            time.sleep(1)
        raise PortOpenError(f"Port {com} is not responding")
    except Exception as E:
        print(f"{E}")
        fileout.close()
