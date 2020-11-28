## Optional arguments of the *declare* function

In addition to the standard two arguments of the `declare` function - ontology relation class and user code object - the user can provide additional keyword arguments that modify the execution of the function. The use of these optional keyword arguments is outlined below.

### **argument1** and **argument2**

The use of these arguments is outlined in docs/declare basic use.md - however they are demonstrated as positional arguments there. They are defined as keyword arguments with default values 0 and 1. These arguments represent the **ordered** pair that is being linked to the arguments of a specific ontology relation.


### **type_mismatch**

The `type_mismatch` argument is set to a default value of `True`. This allows relation-checker to print warning messages when the type of the user's code object is not compatible with the type of the ontology object. For example,

```
    declare(age, 3)

    declare(Student, multiargs)
```

on lines 195 and 197 displays the following warnings:

```
Warning: Mismatching types at line 195 in file PATH_TO_YOUR_FILE: 
<class 'owlready2.prop.DataPropertyClass'> and <class 'int'>

Warning: Mismatching types at line 197 in file PATH_TO_YOUR_FILE: 
<class 'owlready2.entity.ThingClass'> and <class 'function'>
```

However, replacing these lines with

```
    declare(age, 3, type_mismatch= False)
```
and
```
    declare(Student, multiargs, type_mismatch= False)
```

does not display this warning.


### **value_overwrite**

The `value_overwrite` argument is set to a default value of `True`. This allows relation-checker to print warning messages when a class, function or method declaration is being overwritten - another declaration is created for the class, function or method. For example,

```
    declare(Student, Person)

    declare(Teacher, Person)
```

on lines 17 and 19 displays the following warning:

```
Warning: Declaration at line 19 in file PATH_TO_YOUR_FILE :
	  Person has already been declared. The old value is now overwritten.
```

However, replacing these lines with

```
    declare(Student, Person)

    declare(Teacher, Person, value_overwrite= False)
```

does not display this warning, which is supressed by the `value_overwrite= False` assignment.


### **overwrite_handling**

The `overwrite_handling` argument is set to a default value of `True`. This ensures that relation-checker destroys a link between a function or method and an ontology relation when overwriting a declaration. This is distinct from the `value_overwrite` argument, which simply allows or blocks warning messages from being displayed. Here we demonstrate what happens when value_overwrite is not set:

```
    declare(teaches, Person.add_student)
    declare(taught_by, Person.add_student)

    s.add_student(t)
```

These declarations (assume on lines 125, 126 and 128), will yield the following output:

```
Warning: Declaration at line 126 in file PATH_TO_YOUR_FILE :
	  Person.add_student has already been declared. The old value is now overwritten.
```

The link between `Person.add_student` and `teaches` has been destroyed, so there is no inconsistency detected by relation-checker.<br/>
Now we can change the declaration on line 126:

```
    declare(teaches, Person.add_student)
    declare(taught_by, Person.add_student, overwrite_handling= False)

    s.add_student(t)
```

The output has now changed to be the following:

```
Warning: Declaration at line 126 in PATH_TO_YOUR_FILE :
	  Person.add_student has already been declared. Both declarations will be tested.

Error on line 128 in file PATH_TO_YOUR_FILE:
	student.teaches.teacher
Is not allowed in your ontology.
```

The warning message now indicates that both declarations will be tested. Indeed, relation-checker now tests two cases for consistency - when `Person.add_student` is linked to `teaches`, and when `Person.add_student` is linked to `taught_by`. As a result of this, `s.add_student(t)` is reported as an error due to violation of the `teaches` relation.

Appending `t.add_student(s)` on line 129 will result in two errors, as each statement violates one of the two conditions, despite using the same exact `add_student` method.

```
Error on line 129 in file PATH_TO_YOUR_FILE:
	teacher.taught_by.student
Is not allowed in your ontology.

Error on line 128 in file PATH_TO_YOUR_FILE:
	student.teaches.teacher
Is not allowed in your ontology.
```


### **fail_quit**

The `fail_quit` argument is set to a default value of `False`. Keeping `fail_quit` equal to `False` ensures that the program does not terminate if relation-checker identifies an error in consistency with the ontology. This means that when an error message is displayed by the library, the user's code that uses the library will continue to run, concurrent tests are not aborted and further calls to `declare` start other tests. Consider the following code in Sample_code .py:

```
    declare(teaches, x, fail_quit= True)
    x(s, t)
```

The output will be the appropriate error message followed by

```
fail_quit : QUITTING THE PROGRAM
SUCCESS: The process "python.exe" with PID SOME_INTEGER has been terminated.
SUCCESS: The process "python.exe" with PID SOME_INTEGER has been terminated.
SUCCESS: The process "python.exe" with PID SOME_INTEGER has been terminated.
```

with possibly more or less `SUCCESS` messages. These are python processes associated with different relation-checker tests being terminated. The execution of the program stops.

#### **Notes:**
1. The `fail_quit` keyword will not change it's value for function `x` if function `x` gets redeclared. Use this keyword argument with the first `declare` involving `x`.


### **display**

The `display` argument is set to a default value of `None`. If the user chooses to set this argument to `False`, the declare statement is simply ignored.
Supposing that `Person` has been linked to `Student`, and a student `s` has been declared, then the following code

```
    declare(Teacher, Person, display= False)
    s1 = Person("HSDF", 10)
    s1.add_student(s)
```

throws an error, since the `declare` statement is simply ignored. The overwriting warning is not displayed either.<br/>
Setting `display` to `True` adds a string of the form `number_of_line_of_declare_statement : name_of_file_of_the_line` to a list, which can be displayed with the help of the `print_display_lines` function, which is discussed in docs\additional functions .md

In addition to that, `display` also sets the following default values for all subsequent calls to `declare`: `overwrite_handling = True`, `display = True`, `fail_quit = False`.