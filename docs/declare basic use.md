## Basic use of the declare function

The `declare` function is responsible for linking objects in the user's code to each other using logical relations found in the user-defined ontology. This ensures that when functions and methods in the user's code are executed, they are also tested for their consistency with the ontology. Here is our example Ontologies .py file:

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
```

Suppose that we create the following script file in which we will use the relation-checker library:

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
```

Here we link the `Person` class (the one in the above script file) to the `Teacher` class from the ontology. We can add the following line to our script.

```
    declare(teaches, Person.add_student)
```

Now we also linked the add_student method of the `Person` class to the teaches relation of the ontology. This means that whenever the `add_student` method is called in our file, it will do two things:
1. Execute as expected (i.e., it will append an object to the `teaches` list field of a `Person` object)
2. Test for inconsistency in the ontology. If an inconsistency is found, an error message will be displayed.
An inconsistency will be detected if the `domain` and `range` properties of the `teaches` relation are violated. Let us consider the following example - add the following lines to the end of the script file:

```
    t = Person("Harry", 10)

    declare(Student, Person)
    s = Person("Sam", 10)

    s.add_student(t)
```

We have now created a `Person` object `t`, which is automatically linked it to an ontology `Teacher` object (because of the first declaration).<br/>
Next we relinked the `Person` class to the `Student` class from the ontology, and we created a `Person` object `s`, which is now automatically linked to an ontology `Student` object.

Finally we call the `add_student` method, which places `t` into the `teaches` list of `s` (which does not violate Python rules, so it does not crash the program), and displays an error message to the user from the relation-checker library (because here the domain was a `Student` and the range was a `Teacher`). We have attached semantic meaning to the user's code, and in this way we captured a logical error in the script file.

#### **Notes:**
1. When we relinked the `Person` class, relation-checker issued a `Warning: Declaration at line 136 in file PATH_TO_YOUR_FILE :
	  Person has already been declared. The old value is now overwritten.`
2. `t` and `s` could have been declared as two different classes in the script file. The error would be caught regardless, as long as `s` was not linked to a `Teacher` object or `t` was not linked to a `Student` object.
3. The relation-checker error would have been properly thrown as long as `declare(teaches, Person.add_student)` was placed anywhere after the definition of the `Person` class and before `add_student` was called. This statement would impact (i.e. test consistency with the ontology) every execution of `add_student` that followed it.
4. In order for `declare` to work without error, both arguments must be previously linked to ontology objects by `declare` functions. If the function or method is not linked to an ontology relation, no testing can occur.


### **Ontology inheritance**

The inheritance between classes in the ontology are reflected when testing for consistency of the user's code.<br/>
For example, notice that the `ClassClown` class of the ontology inherits from the `Student` class. The reasoner provided by the `owlready2` library accounts for relationships between different classes in an ontology while running its automated reasoner.

Consider adding the following code in the user's script file:

```
    declare(ClassClown, Person)
    declare(taught_by, Person.add_student)

    cc = Person("Dude", 10)
    cc.add_student(t)
```

This code will not throw an error. Although `cc` is linked to a `ClassClown` ontology object, it can be `cc` can be `taught_by` an object (`c`) that is linked to a `Teacher` ontology object. This is because `ClassClown` inherits from `Student` in the ontology, so it satisfies the `domain = [Student]` requirement of the `taught_by` relation.

#### **Notes:**
1. In the code above, the user's script will continue to execute the `add_student` method as defined in the `Person` class. The `Person t` object will be added to the `teaches` list field of the `Person cc` object.


### **Multiple declarations per function**

Certain methods and functions may have more than two arguments, with a set relations that the user may wish to impose on different pairs of arguments. The relation-checker library allows users to link a method or a function to multiple ontology relations. Suppose that we add the following code to the script file:

```
    def multiarg(a, b, c):
        return a + b + c
    
    declare(teaches, multiarg, 0, 1)
    declare(taught_by, multiarg, 1, 2)
    multiarg(s, t, s)
```

We have created a function `multiarg` that has more than two arguments. We then linked the relationship between arguments 0 and 1 of the function to the `teaches` ontology relation, and we linked the relationship between arguments 1 and 2 of the function to the `taught_by` ontology relation.<br/>
Then we call `multiarg` with arguments `s, t, s`, and that line of code issues two errors, one for each pair of declarations (because `s` is linked to a `Student` ontology object and `t` is linked to a `Teacher` ontology object).

The user does not have to link every pair of consecutive arguments. For example, if we remove

```
    declare(teaches, multiarg, 0, 1)
```

then `multiarg(s, t, s)` will only throw one error, associated with the `taught_by` relation violation.

The user can also link non-consecutive arguments:

```
    declare(teaches, multiarg, 0, 2)
```

This is allowable code. If we call `multiarg(s, t, s)`, relation-checker will detect an error because `Student teaches Student` is not allowed by the ontology `teaches` relation.

#### **Notes:**
1. If the user `declare`s a function or method without specifying the arguments to which the ontology relation applies, relation-checker will assume that the user is applying the relation check to arguments 0 and 1.
2. The argument numbers are passed in as positional arguments. However, they are defined as keyword arguments, `argument1` and `argument2`.
3. Notice that (unlike `add_student`) `multiarg` is not a method, but a function. The `declare` function can link both methods and functions to ontology relations.


### **Errors and warnings**

There are different error and warning messages that are displayed by relation-checker. The first of these is the ontology inconsistency error message, such as the following:

```
Error on line 184 in file PATH_TO_YOUR_FILE:
	teacher.taught_by.student
Is not allowed in your ontology.
```

This error is the only non-fatal error provided by relation-checker - this error results from the ontology consistency test that is launched by a call to the `declare` function. The remaining error messages are **fatal issues**, such that the ontology consistency test associated with the issue is not executed. These issues are identified in the `declare` function before the ontology consistency test is executed.
