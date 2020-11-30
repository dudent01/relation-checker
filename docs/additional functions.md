## Additional functions

The relation-checker library provides the user with the following additional functions.

### **disable_print** and **enable_print**

Calling `disable_print` prevents python from printing any output to the console except for the output provided by the relation-checker library.<br/>
Calling `enable_print` reverses that effect, allowing python to print output to the console again. Here is an example of filtering output with the help of these two functions:

```
    disable_print()
    s.add_student(t)
    print("IN")
    enable_print()
    print("OUT")
```

Output:

```
OUT

Error on line 196 in file PATH_TO_YOUR_FILE:
	student.teaches.teacher
Is not allowed in your ontology.
```

#### **Notes:**
1. The error thrown by the library with respect to `s.add_student(t)` is printed after `OUT`, because the identification of the error occurs inside a process different from that in which the user's program itself performs the printing computation.


### **entry_line**

This function allows the user to discover the lines on which a specific ontology object has been `declare`d in the user's code.<br/>
We can call this function as follows: `entry_line(Student)`

This call prints out the following:

```
Student is declared with the following objects on corresponding lines:
Person : 136
Guy : 194
```

Here are the referenced lines:<br/>
136 >> `declare(Student, Person)`<br/>
194 >> `declare(Student, Guy)`

The `entry_line` function has two additional optional keyword arguments.<br/>
The first keyword argument is `object`. This argument allows the user to see only those line numbers where the ontology object was `declare`d to be linked to a specific user source code object.

```
entry_line(Student, object= Person)
```

This code returns the following message:

```
Student is declared on line(s): 136
```

The second keyword argument is `printer`. It is initialized to `True`. The `entry_line` function always returns the list of lines on which `declare` is called, as prompted by the function. If `printer` is set to `False`, the messages will not be printed for the user.


### **print_display_lines**

This function, called without arguments, simply prints out the list of all lines where `declare` is called. Note that only the lines including and following the line at which the `declare` function has the `display` keyword argument set to `True` will be in this list.

The output will look like this:

```
Lines of declaration:
132 : PATH_TO_FILE_WHERE_DECLARATION_IS_MADE
133 : PATH_TO_FILE_WHERE_DECLARATION_IS_MADE
136 : PATH_TO_FILE_WHERE_DECLARATION_IS_MADE
194 : PATH_TO_FILE_WHERE_DECLARATION_IS_MADE
```

From this output we can tell that on line 132, the `declare` function had `display= True`.<br/>
The `declare` function was called only three more times after that line during the execution of the program.

This list is printed out at the very end of the output, regardless of where the `print_display_lines()` function call is placed.


### **print_overwrites**

Like `print_display_lines`, this function also prints a list out at the very end of the output, regardless of where the `print_overwrites()` function call is placed.

The function prints out the lines at which overwrites occur, and the corresponding source code objects that are overwritten. If called from the same file as in the previous example, the output is

```
Overwrites:
[136, 'Person']
```

This is because the first linking of `Person` occurs on line 132 >> `declare(Teacher, Person)`.<br/>
The second linking of `Person` occurs on line 136 >> `declare(Student, Person)`, causing the reported overwrite.

#### **Notes:**
1. This function will also print overwrites of functions / methods.
2. The value of the `overwrite_handler` keyword argument in functions / methods does not impact the appearence of those functions / methods in the overwrites list.


### **set_end**

The call `set_end()` should be placed at the top of the user's source code, inside of the `if __name__ == '__main__'` block, below the `import` statements. This function ensures that all of the errors reported by relation-checker will be printed after all of the output of the source code is printed. This is essentially another filter for separating the two types of output of a program that uses the relation-checker library.
