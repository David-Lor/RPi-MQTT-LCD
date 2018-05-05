
#Native libraries
import threading
from datetime import datetime
#Package modules
from lcd_i2c import lcd_print, lcd_clear

current_element = None #Save the LCDPrint object that's currently being printed

def destroy_current(clear=False):
    if current_element is not None:
        current_element.destroy(clear=clear)
    elif clear:
        lcd_clear()

class LCDPrint(object):
    def __init__(self, lineA, lineB, priority=100, min_time=0, max_time=0, rotate_frequency=0.5, clear_on_destroy=False):
        """
        :param lineA, lineB: lines to print (string, or List of strings for rotary printing)
        :param priority: priority of this message (default=100, higher=more priority)
        :param min_time: min time message must be printed. After time expired, lower priority messages can be printed (default=0 -> do not apply)
        :param max_time: time limit for the message to be printed. After this time, will be erased (default=0 -> do not erase)
        :param rotate_frequency: time between message switching
        :param clear_on_destroy: clear LCD when message is destroyed (default=False)
        Even if clear_on_destroy is False, screen will be cleared if:
         - max_time is defined
         - destroy method is called with "destroy=True" param
        """
        self.lineA = lineA
        self.lineB = lineB
        self.priority = priority
        self.min_time = min_time #TODO IMPLEMENTAR
        if min_time != 0:
            self.created = datetime.now()
        self.max_time = max_time
        self.rotate_frequency = rotate_frequency
        self.rotate_thread = None
        self.rotate_thread_stopEvent = None
        self.maxtime_thread = None
        self.maxtime_thread_stopEvent = None
        self.clear_on_destroy = clear_on_destroy
        self.printed = None #Timestamp when message is printed
        self.print()
    
    def print(self):
        global current_element

        def rotate_f():
            #This function is threaded when ANY of the lines is list (multitext)
            lines = (self.lineA, self.lineB) #lineA/B can be list or string
            types = tuple(type(e) for e in lines)
            print("lines={} | types={}".format(lines, types)) #DEBUG
            if types.count(list) == 1: #One line singletext, one line multitext
                print("one line is multitext") #DEBUG
                singletextLine = lines[types.index(str)]
                lcd_print(singletextLine, lines.index(singletextLine)) #Print singleline
            else: #Both lines multitext
                print("both lines are multitext") #DEBUG
                #nothing else to do here
            #Loop!
            printIndex = [0, 0] #Indexes of texts lines[x] to print
            while not self.rotate_thread_stopEvent.isSet():
                for line in lines:
                    if type(line) is not list:
                        continue #Skip singletext lines
                    lineIndex = lines.index(line)
                    messageIndex = printIndex[lineIndex]
                    message = line[messageIndex]
                    print("imprimo por loop:\nmensaje={}\nlinea={}".format(message, lineIndex))
                    lcd_print(message, lineIndex)
                    #Update printIndex for next loop iteration
                    messageIndex += 1
                    if messageIndex == len(line):
                        messageIndex = 0
                    printIndex[lineIndex] = messageIndex
                self.rotate_thread_stopEvent.wait(timeout=self.rotate_frequency)

        def maxtime_f():
            self.maxtime_thread_stopEvent.wait(timeout=self.max_time)
            self.destroy(clear=True)

        if current_element is not None: #If there's something being printed
            #if self.priority < current_element.priority: #Do nothing if we have less priority than printed element
            if not self.check_priority():
                return
            #else, we can print! but first we must destroy the current element
            current_element.destroy()

        current_element = self #Set this element as current element being printed
        #Check if we must perform rotate line/s. Execute a control thread if so
        if (type(self.lineA), type(self.lineB)) != (str, str): #rotate lines, at least on one line
            #Create the rotating thread
            self.rotate_thread_stopEvent = threading.Event()
            self.rotate_thread = threading.Thread(
                target=rotate_f,
                daemon=True
            )
            self.rotate_thread.start()
        else: #if no rotate lines, just print normal
            lcd_print(self.lineA, 0)
            lcd_print(self.lineB, 1)
        #Create max_time killer thread if needed
        if self.max_time != 0:
            self.maxtime_thread_stopEvent = threading.Event()
            self.maxtime_thread = threading.Thread(
                target=maxtime_f,
                daemon=True
            )
            self.maxtime_thread.start()
    
    def destroy(self, clear=False):
        """Call this method when other print request wants to override this message
        We will set current_element to None, stop our threads and clear LCD screen
        :param clear: Clear screen (default=False)
        """
        global current_element
        current_element = None
        if self.rotate_thread:
            self.rotate_thread_stopEvent.set()
        if self.maxtime_thread:
            self.maxtime_thread_stopEvent.set()
        if self.clear_on_destroy or clear:
            lcd_clear()

    def check_priority(self):
        """Check if the current text can be printed.
        It depends on this object's priority and the current_element priority.
        If current_element has a min_time value and it's been passed, we can print.
        :return: True if it's safe to print
        :return: False if we can't print
        """
        if current_element is None:
            return True
        if self.priority < current_element.priority:
            if current_element.min_time != 0 and (datetime.now() - current_element.created) > current_element.min_time:
                return True
            return False
        return True
