import Ontologies as onto                      # handled in ontology_finder
from Ontologies import *                       # Import needed for access in __main__ script


onto_size = sys.getsizeof(onto)                 # Size of the Ontologies file in bytes
waiting_time = float(onto_size / 2)             # Approximate timeout for reasoner
update_constant = 1.1                           # Constant for extending the time for which the program runs
                                                # Alternatively could be set to (CPUs + 1) / CPUs
                                                # Or keep track of currently active processes and use (num + 1) / num

original_globals = globals()                    # Copy of the globals() dictionary before running __main__

from inspect import getframeinfo, stack
import copy
import importlib
import inspect
from collections import defaultdict
import sys
from sys import platform
import multiprocessing
from multiprocessing import Lock, Value, Manager
import psutil
from traceback import format_exception
from multiprocessing import Process
from queue import Queue

class_names = []
method_names = [item[0] for item in inspect.getmembers(onto) if (inspect.isfunction(item[1]) or type(item[1]) == owlready2.prop.ObjectPropertyClass or type(item[1]) == owlready2.prop.DataPropertyClass)]
instance_names = [item for item in dir(onto) if item[0].islower() and item not in method_names]
instance_variables = []

for name, obj in inspect.getmembers(onto):
    if inspect.isclass(obj):
        class_names.append(name)

classes = defaultdict(None)
methods = defaultdict(None)
instances = defaultdict(None)
lines = defaultdict(dict)

'''
    Enabling and disabling printing of messages
'''
def enable_print():
    sys.stdout = sys.__stdout__

def disable_print():
    sys.stdout = open(os.devnull, 'w')

'''
    This function converts the function, class, or instance variable into its own name as a string
'''
def stringified_name(name):
    if inspect.isfunction(name):
        name_string = str(name)[10:-15]
    elif inspect.isclass(name):
        name_string = name.__name__
    elif str(name)[0:5] == "onto.":
        name_string = str(name)[5:-1]
    else:
        name_string = str(name)                          # Need to fix this up for variables
    return name_string


def entry_line(name, object= None, printer=True):
    '''
    This function (optionally) prints the line at which a specific link was created.
    It also returns the value of the line.

    :param name: The ontology object that was declared
    :param object: The script object that was declared and linked with the ontology object
    :param printer: Default prints messages to user
    :return: THe values of the lines at which objects are linked to ontology
    '''
    sys.stdout = open(os.devnull, 'w') if printer == False else sys.__stdout__      # Enable / disable print statements
    name_samples = lines[name]
    if len(name_samples) == 0:
        print("You have not declared any cases of " + stringified_name(name))
        return None
    if len(name_samples) == 1:
        print(stringified_name(name) + " (only case) is declared on line " + str(list(name_samples.values())[0]))
        return(list(name_samples.values())[0])
    if object != None:
        print(stringified_name(name) + " is declared on line(s): " + str(name_samples[object]))
        return(name_samples[object])
    else:
        print(stringified_name(name) + " is declared with the following objects on corresponding lines:")
        for k, v in name_samples.items():
            print(stringified_name(k) + " : " + str(v))
        return(name_samples)


list_dict_map = {"class_names": classes,
                 "method_names": methods,
                 "instance_names": instances}

'''
    This function returns the name of the list object as a string
'''
def object_name(object):                                    # For globals of current module
    for key, value in list(globals().items()):
        if type(value) == type(object) and value == object:
            return key

'''
    Dictionary to connect specific item in source code to instance of Ontology
'''
item_to_onto = defaultdict(lambda: None)

'''
    Dictionary to ensure that modified __init__ method of a source class is not used in instance_initializer when redeclaring a class
'''
declared_classes = []

if sys.platform == 'win32':
    timer = time.clock
else:
    timer = time.time

display_lines = []
def print_display_lines():
    while(processes.value != 0 or queue_processes.empty() == False):        # Wait for the rest of the program to finish executing
        time.sleep(7)
    if len(display_lines) == 0:
        print('\033[95m' + "You have either not made any declarations, or you forgot to use the display keyword argument in the first declare call." + '\033[0m')
    else:
        print('\033[1m' + "Lines of declaration:" + '\033[0m')
        print(*display_lines, sep= '\n')


def queue_proc_start():
    '''
    Function called by alive to start new processes if other processes failed and the CPUs can handle another process
    '''
    global running
    while queue_processes.empty() == False and running.value < CPUs:
        new_process = queue_processes.get()
        new_process.start()
        running.value += 1
        start_times[new_process] = time.time()
    if (processes.value == 0) and finder('java') and queue_processes.empty():
        killer("java")

def alive(p, lock1):
    '''
    Function to stop a process if it is running.
    If no more processes are left, kill the java.exe process from the Hermit reasoner

    :param p: The python.exe process that has timed out
    '''
    with lock1:
        global running
        running.value -= 1
        p.terminate()
        processes.value -= 1
        queue_proc_start()


def killer(proc_name):
    '''
    Function to stop the python or the java process

    :param proc_name: String representing python or java
    '''
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        sub = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        output, error = sub.communicate()
        for line in output.splitlines():
            if proc_name in str(line):
                pid = int(line.split(None, 1)[0])
                try:
                    os.kill(pid, 0)
                except:
                    pass

    elif platform == "win32" or platform == "win64":
        os.system("taskkill /im " + proc_name + ".exe /f")

def finder(proc_name):
    '''
        Function to check if the python or the java process is running

        :param proc_name: String representing python or java
        '''
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        sub = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        output, error = sub.communicate()
        for line in output.splitlines():
            if proc_name in str(line):
                return True

    elif platform == "win32" or platform == "win64":
        for proc in psutil.process_iter():
            try:
                if proc_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    return False

def process_runner(think, inst1, relation, inst2, calling_line, type1, type2, fail_quit, lock, lock1, procs):
    p = Process(target= think, args= (inst1, relation, inst2, calling_line, type1, type2, fail_quit, lock, procs, ))
    p.start()
    processes.value += 1
    time.sleep(waiting_time)
    alive(p, lock1)


lock = Lock()
lock1 = Lock()

processes = Value('i', 0)
java_killed = Value('i', 0)
value_decremented = Value('i', 0)

def custom_excepthook(exctype, value, traceback):
    '''
    Function to handle errors in the main script. Terminates program on error.
    On error, print error message, kill running java process and kill python process.
    '''
    #for p in multiprocessing.active_children():
    #    p.terminate()
    with lock:
        for line in format_exception(exctype, value, traceback):
            print('\033[91m' + line[:-1] + '\033[0m')
        if finder('java'):
            killer('java')
        killer('python')

sys.excepthook = custom_excepthook

func_args = defaultdict(list)               # Stores the declared arguments for a function, so function cannot be redeclared with other arguments.
enchanced_to_orig = defaultdict(lambda: None)       # Links enchanced function to original function to recognize that function is being redeclared (after it has been declared and enchanced).


overwrites = []

def print_overwrites():
    while (processes.value != 0 or queue_processes.empty() == False):  # Wait for the rest of the program to finish executing
        time.sleep(7)
    if len(overwrites) == 0:
        print('\033[95m' + "You did not overwrite any declarations.")
    else:
        print('\033[1m' + "Overwrites:" + '\033[0m')
        print(*overwrites, sep= '\n')


func_props  = defaultdict(list)      # Lists arguments for functions, used in function_enchancer
start_times = defaultdict(int)       # Start times of the processes

first = True            # Flag indicating that declare is called for the first time
                        # Makes multi_timer thread run

def multi_timer(tested_triples, at_end):
    global running
    while(threading.main_thread().is_alive() or processes.value != 0):
        now = time.time()
        for key in start_times.keys():
            if now >= waiting_time + start_times[key]:
                if key.is_alive():
                    for child in psutil.Process(key.pid).children():
                        child.kill()
                    alive(key, lock1)

        queue_proc_start()
        #print(running.value)
        #print("QUEUE SIZE : " + str(queue_processes.qsize()))
        time.sleep(5)
    now = time.time()
    for key in list(start_times):
        if now >= waiting_time + start_times[key]:
            if key.is_alive():
                alive(key, lock1)
                del start_times[key]
    queue_proc_start()

    for k, v in tested_triples.items():         # Print out the errors that were caught but were the same triple as a printed
        if v[0] == -1:                          #STILL NEED TO SET -1 FOR FAILURES -- ADDING TOO MANY KEYS, STILL NEED TO HANDLE RECURSION
            for val in v[2-at_end.value:]:
                noNum_inst1 = re.sub(r'\d+$', '', k[0])
                noNum_inst2 = re.sub(r'\d+$', '', k[2])
                print('\033[91m' + "Fatal error on line " + '\033[94m' + str(val[0]) + '\033[91m' + " in file " + '\033[94m' + val[1] + '\033[91m' + ":\n\t" + '\033[94m' + noNum_inst1 + '\033[1m' + "." + '\033[95m' + k[1] + '\033[91m' + "." + '\033[94m' + noNum_inst2 + '\033[91m' + "\nIs not allowed in your ontology.\n" + '\033[0m')
        if v[0] == -2:
            for val in v[2 - at_end.value:]:
                print('\033[91m' + "Constraint error on line " + '\033[94m' + str(val[0]) + '\033[91m' + " in file " + '\033[94m' + val[1] + '\033[91m' + ":\n\t" + '\033[94m' + stringified_name(
                    val[2]) + '\033[91m' + ": instance variable " + '\033[94m' + str(k[1]) + '\033[91m' + " = " + '\033[94m' + str(k[2]) + '\033[91m' + " violates the ontology constraint " + '\033[94m' + k[0] + '\033[91m' + ".\n" + '\033[0m')

#tested_triples = defaultdict(list)            # Stores the ontology triples and their passed/failed status (True/False)
queue_processes = Queue()                     # FIFO queue of processes, to ensure that only as many processes as CPUs run at a time
CPUs = multiprocessing.cpu_count()            # Number of CPUs

running = Value("i", 0)                                         # Number of processes running right now
#fail_indicators = []                            # multiprocessing.Value values that can be passed to processes to determine failure

at_end = Value('b', False)                      # Set to True to make errors print out at the end of execution
def set_end():
    global at_end
    at_end.value = True

onto_properties = defaultdict(list)             # Classes mapped to instance variables that are linked to data properties
                                                # Each value is a pair (data property, instance variable name)