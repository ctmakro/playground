def sizeof(k):
    import sys
    return sys.getsizeof(k)

def nc(name, attrs):
    attrs = attrs.split(' ')

    code = '''
class {classname}():
    __slots__ = {slotstring}
    def __init__(self, {variables}):
        {variable_assignments}

__created = {classname}
    '''.format(
            classname = name,
            slotstring = repr(attrs),
            variables = ','.join(attrs),
            variable_assignments = ';'.join(
                ['self.{v} = {v}'.format(v=a)
                for a in attrs])
        )

    exec(code, globals())
    return __created

class slotful(type):
    def __new__(self, name,
                parents, attrs):
        if '__slots__' not in attrs:
            attrs['__slots__'] = ()

        print(attrs)
        return type(name, parents, attrs)

class a(metaclass=slotful):
    __slots__ = 'b'
    def __init__(self):
        self.b = 1

class b(a, metaclass=slotful): pass

P = nc('P','j k')
pp = P(9,8)
# pp.j = 1
print(pp.j)
pp.k = 2

j = b()
print(b.__slots__)
b.b=3
b.k=4

print(j.__class__)
# print(pp.__class__.__name__)
print(pp.__class__)

print(sizeof(j))
print(sizeof(pp))
