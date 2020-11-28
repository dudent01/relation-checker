## Imported and recursive functions

### **Imported functions**

The relation-checker library can not only handle functions from the user's script file, but also from files that are imported into the main script file.<br/> Suppose that we create a python file called Importable .py:

```
from relation-checker import *

def inner_imp(a, b):
    pass

def imp_func(a, b):
    inner_imp(a, b)

def gimp_func(a, b):
    inner_imp(a, b)

def wrong():
    x = 1/0
```

We can import this file into our main file Sample_code.py:

```
if __name__ == '__main__':
    from relation-checker import *
    from Importable import *
```

Then we once again create the `Person` class, and use the `declare` function to link it to `Teacher`, create an instance `t`, relink it to `Student`, and create another instance `s`.

```
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
```

Then we can link the function `imp_func` from Importable .py to the `taught_by` relation and call it:

```
    declare(taught_by, imp_func)
    imp_func(t, s)
```

An error is detected, because object `t` cannot be `taught_by` object `s`. The linking was successful.<br/>
The `declare(taught_by, imp_func)` could also be done inside Importable .py, after `imp_func` is defined.

Suppose that instead of `declare(taught_by, imp_func)` in Sample_code .py, we link `inner_imp` to `taught_by` directly inside of the Importable .py file. Since `inner_imp` is called by `imp_func`, we expect such a declaration to check the consistency of the call to `imp_func` in the Sample_code .py file. We can access `declare` because we have imported relation-checker in the Importable .py file. Now we have two options:
1. We can `declare(taught_by, inner_imp)` directly after the definition of `inner_imp`. This means that if we call both `imp_func(t, s)` and `gimp_func(t, s)` in the Sample_code .py, relation-checker will identify errors in both cases.
2. We can `declare(taught_by, inner_imp)` inside the `imp_func(t, s)` function. In this case, a link between `inner_imp` and the `taught_by` ontology relation is established only in the scope of `imp_func`, so relation-checker will identify an error for the call `imp_func(t, s)`, but not for `gimp_func(t, s)`, despite `gimp_func` calling `inner_imp`.

#### **Notes:**
1. If `inner_imp` function is linked to an ontology relation and an error is thrown, then because `inner_imp` is directly called only inside Sample .py, the error message will refer the user to the Sample .py file, and to the line at which `inner_imp` is called in the Sample .py file.

### Imported function errors

Suppose that there is an error in a function that is being imported. In our example, the function `wrong` computes `1/0`, which (unless you have studied complex analysis) is wrong. This is an error beyond the scope of relation-checker. Calling the imported `wrong` function in Sample_code .py will result in python finding the error and terminating the program. This case is no different from the case of making a python error directly in the main file (Sample_code .py) - the program will terminate, and all processes launched by relation-checker will terminate as well.


### **Recursive functions**

While the entire depth of the recursion of a recursive function is executed by the python interpreter, relation-checker does not redundantly check the consistency of the recursive function with the ontology. It only checks the function once for every pairwise relation that is linked to the function's arguments by the user. When displaying an error message, relation-checker directs to the line at which the recursive function is called in the script, not where it is called in the recursive function's definition. Consider the following code inside the Sample_code .py file:

```
    def recurse(i, j):
        if i.age == 0:
            return
        print(j.age)
        i.age -= 1
        recurse(i, j)
```

We then link `recurse` to the `taught_by` ontology relation and make a call to this function, using the previously defined `t` and `s` objects:

```
    declare(taught_by, recurse)
    recurse(t, s)
```

Recall that `t = Person("Harry", 10)`, so `t.age` is equal to 10.<br/>
Assuming that `recurse(t, s)` is on line 184 of Sample_code .py, the following error message is displayed:

```
Error on line 184 in file PATH_TO_YOUR_FILE:
	teacher.taught_by.student
Is not allowed in your ontology.
```