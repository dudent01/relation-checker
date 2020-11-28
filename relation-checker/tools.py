from utils import *
import threading
import _thread as thread
import os
from multiprocessing import Process
import csv
import psutil
import signal
import re

'''
    Functions for creating the link
'''
def link_maker(name, object, argument1, argument2, cls, tm, vo, oh, onto_properties):
    '''
    This function creates a link between the user's script and an ontology entity.
    This function should be called after a variable is introduced in the code to link that variable to the Ontology.
    This function should be called for a method before the method is first used.
    This function can be called on an instance variable only after it's class has been declared.

    :param name: The entity from the Ontology that the object is being linked to
    :param object: The name of the variable from the script that is being linked to the Ontology
    :param cls: Optional argument, the class of which object is an instance variable
    :param tm: Optional argument, set to False to turn off type mismatch warnings
    :param vo: Optional argument, set to False to turn off value overwrite warnings
    :param oh: Optional argument, set to False if you want declaration to not stop another declaration that it overwrites
    :return:
    '''
    if object == None:
        pass                                                            # Needs to be modified for automatic object recognition from line below

    name_string = stringified_name(name)
    calling_line = getframeinfo(stack()[2][0]).lineno                   # Line from which script calls the declare function
    calling_file = getframeinfo(stack()[2][0]).filename                 # File in which function is called

    # Ensure that the name of the Ontology element is in the Ontology
    if name_string not in original_globals.keys():
        print('\033[91m' + "Fatal issue on line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ":\n\t  " + '\033[0m')
        print('\033[94m' + name_string + '\033[91m' + " is not a member of the ontology.")
        print('\033[91m' + "You cannot use it as the first argument to the declare() function.")
        exit(1)

    orig_name = original_globals[name_string]                           # To avoid confusion in case of duplicate name in script

    # Handle case when class argument is provided, used to catch errors in arguments
    if cls != None:
        if cls not in classes.keys():
            print('\033[91m' + "Fatal issue on line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ":\n\t  " + '\033[0m')
            print('\033[94m' + stringified_name(cls) + '\033[91m' + " is not a defined class.")
            print( "Please " + '\033[94m' + "declare(some_class , " + stringified_name(cls) + ")" + '\033[91m' + " before this statement." + '\033[0m')
            exit(1)
        if (stringified_name(object) not in instance_variables):# and stringified_name(object) not in cls.__init__.__code__.co_varnames):
            print('\033[91m' + "Fatal issue on line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ":\n\t  " + '\033[0m')
            print('\033[94m' + stringified_name(object) + '\033[91m' + " is not an attribute of class " + '\033[94m' + str(cls.__name__) + '\033[0m')
            exit(1)
        else:
            onto_properties[cls].append((name_string, stringified_name(object)))

    if tm == False:
        disable_print()

    # Issue warnings for type mismatches in arguments
    while(True):
        if ((type(orig_name) == owlready2.prop.ObjectPropertyClass or type(orig_name) == owlready2.prop.DataPropertyClass) and inspect.isfunction(object)):
            break
        if (object in instance_variables):          # Needs to be changed to account for type of variable declared
            break
        if (inspect.isclass(object) and inspect.isclass(type(orig_name)) != inspect.isclass(type(object))):
            print('\033[1m' + "Warning:" + '\033[91m' + " Mismatching types at line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ": \n" + '\033[94m' + str(type(orig_name)) + '\033[91m' + " and " + '\033[94m' + str(type(object)) + '\n\033[0m')
            break
        if (inspect.isclass(object) != inspect.isclass(orig_name)):
            print('\033[1m' + "Warning:" + '\033[91m' + " Mismatching types at line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ": \n" + '\033[94m' + str(type(orig_name)) + '\033[91m' + " and " + '\033[94m' + str(type(object)) + '\n\033[0m')
            break
        if (inspect.isclass(object) and inspect.isclass(type(orig_name)) == inspect.isclass(type(object))):
            break
        if (inspect.isfunction(object) == False and inspect.isfunction(orig_name) == False and inspect.isclass(object) == False and inspect.isclass(type(object)) and inspect.isclass(type(orig_name)) == inspect.isclass(type(object)) and inspect.isclass(orig_name) == inspect.isclass(object)):
            break
        if (type(orig_name) != type(object)):
            print('\033[1m' + "Warning:" + '\033[91m' + " Mismatching types at line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ": \n" + '\033[94m' + str(type(orig_name)) + '\033[91m' + " and " + '\033[94m' + str(type(object)) + '\n\033[0m')
            break
        break

    enable_print()

    lines[name][object] = calling_line                                  # Helps the entry_line function

    if vo == False:
        disable_print()

    # Ensure that the script object is not taken directly from the Ontology
    if stringified_name(object) in original_globals.keys():
        if object == orig_name:
            print('\033[91m' + "Fatal issue on line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m'  + ":\n\t  " + '\033[0m')
            print('\033[94m' + stringified_name(object) + '\033[91m' + " is a member of the ontology - it is not redefined in your script.")
            print('\033[91m' + "You cannot use it as the second argument to the " + '\033[94m' + "declare()" + '\033[91m' + " function.\n")
            exit(1)

    warning = 0
    for name_list in [method_names, class_names, instance_names]:
        # If script object is being reassigned to another Ontology entity, delete the reference to the previous Ontology entity
        if enchanced_to_orig[object] in list_dict_map[object_name(name_list)].keys() and [argument1, argument2, name_list] in func_args[enchanced_to_orig[object]]:
            if warning == 0:
                if oh == True:
                    print('\033[1m' + "Warning:" + '\033[91m' + " Declaration at line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + " :\n\t  " + '\033[94m' + stringified_name(enchanced_to_orig[object]) + '\033[91m' + " has already been declared. The old value is now overwritten.\n" + '\033[0m')
                else:
                    print('\033[1m' + "Warning:" + '\033[91m' + " Declaration at line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + " :\n\t  " + '\033[94m' + stringified_name(enchanced_to_orig[object]) + '\033[91m' + " has already been declared. Both declarations will be tested.\n" + '\033[0m')
                overwrites.append([calling_line, stringified_name(enchanced_to_orig[object])])
                warning += 1
            del list_dict_map[object_name(name_list)][enchanced_to_orig[object]]
        else:
            func_args[enchanced_to_orig[object]].append([argument1, argument2, name_list])      # Name list ensures that warning is not throws erraneously if object is in multiple lists

        # Specifically for the appropriate list
        if name_string in name_list:
            if name_list != instance_names:
                list_dict_map[object_name(name_list)][enchanced_to_orig[object]] = copy.copy(orig_name)         # Shallow copy allows to create distinct objects from same Ontology object
            else:
                # Instance names keyed by calling line, since instance values change
                list_dict_map[object_name(name_list)][calling_line] = copy.copy(orig_name)                    # Proposed to replace object with calling_line because variable can change
                count = 0
                for line in lines.keys():
                    if lines[line][object]:
                        count += 1
                # If the variable has been declared before, issue a warning, and delete it from instances
                if count > 1:
                    print('\033[1m' + "Warning:" + '\033[91m' + " Declaration at line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + " : " + '\033[94m' + stringified_name(
                        enchanced_to_orig[object]) + '\033[91m' + " has already been declared. The old value is now overwritten." + '\033[0m')
                    for line in lines.keys():
                        if lines[line][object] != calling_line:
                            del instances[lines[line][object]]
                            overwrites.append([calling_line, stringified_name(enchanced_to_orig[object])])

            # If the object is a class and it is from the script, add it to the script's globals and add the instance variables to the script's globals
            if name_list == class_names and type(object) != owlready2.prop.DataPropertyClass and type(object) != owlready2.prop.ObjectPropertyClass:   # Adds class to globals and then adds instance variables to globals, avoids owl objects
                inspect.stack()[2][0].f_globals[stringified_name(object)] = object
                try:
                    instance = inspect.stack()[2][0].f_globals[stringified_name(object)].__init__.__code__.co_names
                    for i in instance:
                        inspect.stack()[2][0].f_globals[i] = i
                        instance_variables.append(i)
                except:
                    inspect.stack()[2][0].f_globals[stringified_name(object)] = object              # Set global to object, not stringified name

            if name_list == method_names:
                if oh == True:
                    position = 0
                    for func in func_props[enchanced_to_orig[object]]:
                        if func[1] == argument1 and func[2] == argument2:
                            del func_props[enchanced_to_orig[object]][position]
                        position += 1
                func_props[enchanced_to_orig[object]].append([methods[enchanced_to_orig[object]], argument1, argument2])

'''
    Function that uses sync_reasoner() to find inconsistencies in the source code
'''
def think(inst1, relation, inst2, calling_line, type1, type2, fail_quit, lock, processes, running, calling_file, tested_triples, at_end):
    lock.acquire()
    onto1 = type1()
    onto2 = type2()
    exec("onto1" + "." + relation + ".append(" + "onto2" + ")")
    lock.release()
    try:
        sync_reasoner(debug=0)             # Debug = 0 to avoid printing messages

    except:
        lock.acquire()
        noNum_inst1 = re.sub(r'\d+$', '', inst1[5:])
        noNum_inst2 = re.sub(r'\d+$', '', inst2[5:])
        if at_end.value == 0:
            print('\033[91m' + "Error on line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ":\n\t" + '\033[94m' + noNum_inst1 + '\033[1m' + "." + '\033[95m' + relation + '\033[91m' + "." + '\033[94m' + noNum_inst2 + '\033[91m' + "\nIs not allowed in your ontology.\n" + '\033[0m')

        processes.value -= 1

        tested_triples[(noNum_inst1, relation, noNum_inst2)] = [-1, *tested_triples[(noNum_inst1, relation, noNum_inst2)][1:]]        # Set fail indicator to -1

        if fail_quit:
            print('\033[1m' + "fail_quit : QUITTING THE PROGRAM" + '\033[0m')
            if finder('java'):
                killer("java")
            killer("python")

        lock.release()
    finally:
        running.value -= 1

'''
    Function that uses sync_reasoner() to find violations of DataProperty constraints
'''
def constraint(constr, onto_inst, type_onto_inst, running, at_end, lock, calling_line, calling_file, fail_quit, tested_value, processes, inst_name, tested_triples):
    lock.acquire()
    onto_inst = type_onto_inst()
    exec("onto_inst" + "." + constr + " = " + str(tested_value))
    lock.release()
    try:
        sync_reasoner(debug=0)
    except:
        lock.acquire()
        if at_end.value == 0:
            print('\033[91m' + "Constraint error on line " + '\033[94m' + str(calling_line) + '\033[91m' + " in file " + '\033[94m' + calling_file + '\033[91m' + ":\n\t" + '\033[94m' + stringified_name(onto_inst) + '\033[91m' + ": instance variable " + '\033[94m' + inst_name + '\033[91m' + " = " + '\033[94m' + str(tested_value) + '\033[91m' + " violates the ontology constraint " + '\033[94m' + constr + '\033[91m' + ".\n" + '\033[0m')

        tested_triples[(constr, inst_name, tested_value)] = [-2, *tested_triples[(constr, inst_name, tested_value)][1:]]

        processes.value -= 1

        if fail_quit:
            print('\033[1m' + "fail_quit : QUITTING THE PROGRAM" + '\033[0m')
            if finder('java'):
                killer("java")
            killer("python")

        lock.release()
    finally:
        running.value -= 1

'''
    Functions for testing the label against the Ontology
'''
def function_enhancer(fn, fail_quit, procs, argument1, argument2):
    def new_function(*args, **kwargs):
        fn(*args, **kwargs)
        #print("New")                            # This is where the checking against Ontology is defined
                                                # Do try/except to check for an error
                                                # Build an ontology for the model in Ontologies.py
        if getframeinfo(stack()[1][0]).function == fn.__name__:         # Identifies recursion
            return
        relevant_ops = func_props[enchanced_to_orig[fn]]
        calling_file = getframeinfo(stack()[1][0]).filename
        for operation in relevant_ops:
            relation = stringified_name(operation[0])
            arg1 = args[operation[1]]
            arg2 = args[operation[2]]
            inst1 = item_to_onto[arg1]
            inst2 = item_to_onto[arg2]
            calling_line = getframeinfo(stack()[1][0]).lineno                                       # Line of error for think() in case of error

            #exec("inst1" + "." + stringified_name(relation) + ".append(" + "inst2" + ")")
    #    p = threading.Thread(target=think, args= (inst1, relation, inst2, calling_line), daemon= True)
    #    p.start()
        #p.join(timeout= waiting_time)
    #    timer = threading.Timer(waiting_time, p.join, kwargs={'timeout' : 0})
    #    timer.start()
            #global fail_indicators
            #fail_indicators.append(Value('i', 0))
            noNum_inst1 = re.sub(r'\d+$', '', str(inst1)[5:])
            noNum_inst2 = re.sub(r'\d+$', '', str(inst2)[5:])
            global tested_triples
            if (noNum_inst1, stringified_name(relation), noNum_inst2) in tested_triples.keys():       # Need to identify recursion
                tested_triples[(noNum_inst1, stringified_name(relation), noNum_inst2)] = tested_triples[(noNum_inst1, stringified_name(relation), noNum_inst2)] + [[calling_line, calling_file]]
                continue
            else:
                tested_triples[(noNum_inst1, stringified_name(relation), noNum_inst2)] = [0, [calling_line, calling_file]]
            global running
            global at_end
            p = Process(target= think, args= (str(inst1), stringified_name(relation), str(inst2), calling_line, type(inst1), type(inst2), fail_quit, lock, procs, running, calling_file, tested_triples, at_end ))
            processes.value += 1
            if processes.value > CPUs:
                queue_processes.put(p)
                start_times[p] = 0
            else:
                p.start()
                start_times[p] = time.time()
                running.value += 1

    enchanced_to_orig[new_function] = fn
    return new_function

'''
    Function for creating new Ontology instance
'''
def instance_initializer(initializer, item_to_onto, onto_properties, fail_quit, procs, object):
    def new_function(*args, **kwargs):
        initializer(*args, **kwargs)
        #print("New")                            # This is where the instance is created in the Ontology
        cls_name = stringified_name(initializer).split('.')[0]
        cls = inspect.stack()[1][0].f_globals[cls_name]
        cls_onto = classes[cls]
        instance = cls_onto()
        item_to_onto[args[0]] = instance                              # Create the new ontology instance for self of initializer
        calling_file = getframeinfo(stack()[1][0]).filename
        calling_line = getframeinfo(stack()[1][0]).lineno
        global tested_triples
        global running
        global at_end
        global tested_triples
        #print(args)
        #print(initializer.__code__.co_varnames)
        try:
            for constr in onto_properties[cls]:                        # constr is a string of the name of the DataProperty constraint corresponding to an instance variable
                index = initializer.__code__.co_varnames.index(constr[0])
                inst_name = constr[1]
                tested_value = args[0].__dict__[inst_name]                              # args[0] is the declared object
                if (constr[0], constr[1], tested_value) in tested_triples.keys():
                    tested_triples[(constr[0], constr[1], tested_value)] = tested_triples[(constr[0], constr[1], tested_value)] + [[calling_line, calling_file]]
                    continue
                else:
                    tested_triples[(constr[0], constr[1], tested_value)] = [0, [calling_line, calling_file, stringified_name(instance)]]
                p = Process(target= constraint, args= (constr[0], stringified_name(instance), type(instance), running, at_end, lock, calling_line, calling_file, fail_quit, tested_value, procs, inst_name, tested_triples))
                processes.value += 1
                if processes.value > CPUs:
                    queue_processes.put(p)
                    start_times[p] = 0
                else:
                    p.start()
                    start_times[p] = time.time()
                    running.value += 1
        except:
            pass
    return new_function


'''
    display makes sure that only the declarations up to the one marked with display True will be in effect
                                     declarations marked with display False will not be in effect
    Otherwise all declarations are in effect
'''
def declare(name, object, argument1 = None, argument2 = None, cls = None, type_mismatch= None, value_overwrite= None, overwrite_handling= None, display= None, fail_quit= None):
    if type_mismatch == None:
        type_mismatch = True
    if value_overwrite == None:
        value_overwrite = True
    if overwrite_handling == None:
        overwrite_handling = True
    if fail_quit == None:
        fail_quit = False
    if argument1 == None:
        argument1 = 0
    if argument2 == None:
        argument2 = 1

    procs = processes

    if display == False:
        return
    if display == True:
        declare.__defaults__ = ("", "", None, None, None, None, None, True, True, False)
        display_lines.append(str(getframeinfo(stack()[1][0]).lineno) + " : " + str(getframeinfo(stack()[1][0]).filename))

    if stringified_name(object) != 'function_enhancer.<locals>.new_function':
        enchanced_to_orig[object] = object

    global first
    if first == True:
        first = False
        global tested_triples
        tested_triples = Manager().dict()
        global at_end
        time_all = threading.Thread(target= multi_timer, args=(tested_triples, at_end ))
        time_all.start()


    global onto_properties
    link_maker(name, object, argument1, argument2, cls, type_mismatch, value_overwrite, overwrite_handling, onto_properties)
    if object in list_dict_map[object_name(method_names)].keys():
        if '.' not in stringified_name(object):
            inspect.stack()[1][0].f_globals[stringified_name(object)] = function_enhancer(object, fail_quit, procs, argument1, argument2)
        else:
            cl_meth = stringified_name(object).split('.')
            cl = cl_meth[0]
            meth = cl_meth[1]
            cla = inspect.stack()[1][0].f_globals[cl]
            setattr(cla, meth, function_enhancer(object, fail_quit, procs, argument1, argument2))
        return

    #global changed
    global declared_classes
    global ini
    if object in list_dict_map[object_name(class_names)].keys():
        if object not in declared_classes:
            ini = object.__init__
            declared_classes.append(object)
        setattr(object, '__init__', instance_initializer(ini, item_to_onto, onto_properties, fail_quit, procs, object))