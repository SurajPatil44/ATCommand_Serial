import msvcrt
import sys
import threading
from enum import Enum
import signal
import time
from queue import Queue


class ProcessCommand:

    def __init__(self,cmd_q = None):
        self.PressedA = False
        self.GotAT = False
        #self.first = False
        self.user_q = Queue()
        self.command_q = cmd_q

    def get_chars(self):
        try:
            while True:
                #print("waiting here")
                pressedKey = msvcrt.getche()
                self.user_q.put(pressedKey)
                if pressedKey == b'\x03':
                    break
        except Exception as E:
            pass

    def process_chars(self):
        try:
            command = bytearray()
            while True:
                pressedKey = self.user_q.get()
                #print(f"command so far {command}")
                #print(f"{pressedKey.decode()}")
                #print(f"{pressedKey == b'a'}")
                if pressedKey:
                    if pressedKey == b'a' or pressedKey == b'A' and not self.PressedA:
                        if not self.GotAT:
                            self.PressedA = True
                            command += pressedKey
                        else:
                            if self.GotAT:
                                command += pressedKey
                            else:
                                command.clear()    
                    elif self.PressedA and pressedKey == b't' or pressedKey == b'T':
                            self.pressedA = False
                            self.GotAT = True
                            command += pressedKey
                    elif pressedKey == b"\r":
                            if not command:
                                continue
                            #print("atleast here")
                            else:
                                cmd = bytes(command)
                                #print(f"{cmd}")
                                if self.command_q != None:
                                    self.command_q.put(cmd)
                                command.clear()
                                self.GotAT = False
                    elif pressedKey == b'\x03':
                        print("pressed ctrl + c")
                        break
                    else:
                        self.PressedA = False 
                        if self.GotAT:
                            command += pressedKey
                self.user_q.task_done()
            print("done with thread")
        except Exception as E:
            print(f"from process {E}")


    def run(self):
        try:
            T1 = threading.Thread(target=self.get_chars,args=())
            T2 = threading.Thread(target=self.process_chars,args=())
            #T1.daemon = True
            #T2.daemon = True
            T1.start()
            T2.start()
            T1.join()
            T2.join()
            #print("herrrrrreeeee")
            raise KeyboardInterrupt
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("exiting..............")
            while not self.command_q.empty():
                print(self.command_q.get())
                self.command_q.task_done()
            sys.exit(1)
        except Exception as E:
            print(f"from run {E}")
            sys.exit(1)


def signal_hdlr(signum,frame):
    print("getting ctrl + c atleast")
    sys.exit(1)
                

if __name__ == "__main__":
    #signal.signal(signal.SIGINT,signal_hdlr)
    write_q = Queue()
    try:
        PC = ProcessCommand(write_q)
        PC.run()
    except Exception as E:
        print(write_q)
        print(f"{E}")
        sys.exit(0)

