## relation-checker

relation-checker is a library for semantic dynamic code analysis in Python 3. It allows the user to create an ontology specifying a set of semantic relationships and to link the ontology to objects in the user's source code, catching logical errors that could otherwise be unnoticed.

relation-checker uses the owlready2 library to build an ontology and to run a reasoner on it. Here we create a simple ontology.:

```
import owlready2
from owlready2 import *
owlready2.JAVA_EXE = PATH_TO_java.exe_ON_COMPUTER

school = get_ontology("https://test.org/onto.owl")      # Ontology namespace

with school:

    #                                   Declaring ontology objects
    class Person(Thing):
        namespace = school

    class Student(Person):
        namespace = school

    class Teacher(Person):
        namespace = school

    class ClassClown(Student):
        namespace = school
    
    #                                   Declaring ontology relations
     class teaches(ObjectProperty):
        domain = [Teacher]
        range = [Student]

    class taught_by(ObjectProperty):
        domain = [Student]
        range = [Teacher]
        inverse_property = teaches
```

#### **Notes:**
1. This file must be called Ontologies .py and it **must be placed in the relation-checker folder of the library**.
2. None of the ontology object class names end in digits (0-9)
3. Java has to be installed in your system for use of this library.

We can now write a simple script in another file and link it to the ontology:

```
if __name__ == '__main__':
    from relation-checker import *

    class Person:
        def __init__(self, name, age):
            self.teaches = []
            self.name = name
            self.age = age

        def add_student(self, other):
            self.teaches.append(other)


    declare(Teacher, Person)
    declare(teaches, Person.add_student)
    t = Person("Harry", 10)

    declare(Student, Person)
    s = Person("Sam", 10)

    s.add_student(t)
```

#### **Notes:**
1. The imports, declarations, instance definitions, class definitions, and function calls are done inside of the ***if __name__ == '__main__'*** block.
2. The imports are at the top of the ***if __name__ == '__main__'*** block.
3. Declarations can only be made after the function, method, or class has been defined.
4. The Ontologies .py file has to be created in order for this script to run properly.

This script first links the `Person` class from the script itself to the `Teacher` class from the ontology (in the first `declare` statement). It then links the `add_student()` method from the `Person` class to the `teaches` relation from the ontology. Two `Person` objects, both linked to separate `Teacher` ontology objects are created.<br/>
The script then relinks the `Person` class to the `Student` class from the ontology and creates two more Person objects, both linkd to separate `Student` ontology objects. The `add_student()` method is not redeclared, so it remains linked to the `teaches` relation.<br/>
Finally, the `add_student()` method is called. Its two arguments are `Person s` and `Person t`. The method executes as defined in the script. However, the following error message is generated:

```
Error on line 21 in file PATH_TO_YOUR_SCRIPT:
	student.teaches.teacher
Is not allowed in your ontology.
```

This is because `add_student()` takes in two arguments: `s` and `t` which are mapped to the `domain = [Teacher]` and `range = [Student]` of the ontology's `teaches` relation, respectively. The function call maps `s` to an instance of `Student`, which cannot be the domain of `teaches`. The mapping of `t` to an instance of `Teacher` similarly violates the range requirement.

#### **Notes:**
1. `s.add_student(s)` and `t.add_student(t)` would also cause an error, displaying the appropriate error message.
2. These errors will not stop the execution of your script, and they will not stop the execution of any further declarations in your script.

relation-checker also allows the user to link multiple pairs of arguments to different ontology relations:

```
if __name__ == '__main__':
    from relation-checker import *

    class Person:
        def __init__(self, name, age):
            self.teaches = []
            self.name = name
            self.age = age

        def add_student(self, other):
            self.teaches.append(other)

    def multiarg(a, b, c):
        pass

    declare(Teacher, Person)
    declare(teaches, Person.add_student)
    t = Person("Harry", 10)
    
    declare(Student, Person)
    s = Person("Sam", 10)
    
    declare(teaches, multiarg, 0, 1)
    declare(taught_by, multiarg, 1, 2)
    multiarg(s, t, s)
```

This script links the pair of arguments 0 and 1 of `multiarg` to the `teaches` ontology relation, and links the pair of arguments 1 and 2 to the `taught_by` ontology relation. Two errors occur (they again do not stop the execution of the script):

```
Error on line 25 in file PATH_TO_YOUR_SCRIPT:
	student.teaches.teacher
Is not allowed in your ontology.

Error on line 25 in file PATH_TO_YOUR_SCRIPT:
	teacher.taught_by.student
Is not allowed in your ontology.
```

#### **Notes:**
1. There are two errors here because both pairs violate their linked relations. `multiarg(t, s, s)` would raise only one error:

```
Error on line 25 in file PATH_TO_YOUR_SCRIPT:
	student.taught_by.student
Is not allowed in your ontology.
```

If an error occurs inside of the user's program independently of relation-checker, the program and the relation-checker processes will terminate. In this case, several messages such as `SUCCESS: The process "python.exe" with PID AN_INTEGER has been terminated.` may appear. They are of no concern for the user.

relation-checker declarations can also be applied to functions imported into the main script. The declaration for a function has to be made in the file in which the function is defined or directly called. A more thorough demonstration can be found in the docs. The associated error messages indicate the file in which the ontology error has occured.

relation-checker also provides additional functions for the user. `enable_print` and `disable_print` allow the user to isolate the output of the ontology errors from the output of the code. `print_display_lines` displays the lines at which declarations are made at the end of the program's execution, and `print_overwrites` does the same for declarations that are overwritten in the code. `entry_line` returns and optionally prints the number of the line at which a specific declaration is made. `set_end` ensures that ontology errors are displayed only after they are all found at the very end of the program. **Check the docs for proper usage of all of these additional functions.**

**It is possible that the library throws the following error when you first use it:**
```
sync_reasoner: Could not reserve enough space for SOME_INTEGER KB object heap
```

This means that there is not enough memory on your JVM. You should then go to the owlready2 reasoner .py file and decrease `JAVA_MEMORY`. For example, you can decrease it from the default 1000 to 500.

relation-checker is a multiprocessed library. It executes the testing of each call to a declared function in a separate process. However, performance will not decline with an increased number of calls to declared functions, because the processes are managed to run with minimal interference.

The execution is further optimized by caching argument-relation-argument triples, thus displaying errors for methods without recomputing them. Recursive function calls are identified and reported only once to avoid redundancy.

**Read the docs/ directory for further documentation.**