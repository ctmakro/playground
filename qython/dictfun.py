from blist import sorteddict
from collections import namedtuple

def inc_char(char):
    return chr(ord(char)+1)

class DBIter:
    def __init__(self, list, begin, length, asc):
        self.list = list
        self.begin = begin
        self.length = length
        self.asc = asc

        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        length = self.length
        counter = self.counter
        if length == 0:
            raise StopIteration()
        else:
            if self.asc:
                if counter >= length:
                    raise StopIteration()
                else:
                    got = self.list.get_index(self.begin + counter)
                    self.counter+=1
            else:
                if counter >= length:
                    raise StopIteration()
                else:
                    got = self.list.get_index(self.begin - counter)
                    self.counter+=1
        return got

    def skip(self, n):
        self.counter += n

    def __len__(self):
        return self.length

class DB(sorteddict):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.keys_view = self.keys()

    def prefix_left(self, prefix):
        kv = self.keys_view
        return kv.bisect_left(prefix)

    def prefix_right(self, prefix):
        kv = self.keys_view
        return kv.bisect_left(prefix[:-1] + inc_char(prefix[-1]))

    def get_index(self, index):
        kv = self.keys_view
        key = kv[index]
        return key, self.get(key)

    def get_iter(self, prefix, asc=None, desc=None):
        if len(prefix)<1:
            start = 0
            end = len(self) # '' indicates all keys
        else:
            start = self.prefix_left(prefix)
            end = self.prefix_right(prefix)

        length = end-start

        if asc is None:
            if desc is None:
                asc = True
            elif desc:
                asc = False

        dbiter = DBIter(
            list = self,
            begin = start if asc else (end - 1),
            length = length,
            asc = True if asc else False
        )
        return dbiter

    def put(self, key, value):
        self[key]=value

    def get(self, key):
        if key in self:
            return self[key]
        return None

db = DB()

db['user.0001'] = 'Alice'
db['user.0002'] = 'Charlie'
db['user.0003'] = 'Bob'
db['user.'] = 'Test'
db['user'] = 'Test'
db['user0001'] = 'Test'
db['username.0001'] = 'Alice'
db['username.0002'] = 'Charlie'
db['username.0003'] = 'Bob'

db['post.0001'] = 'k'
db['post.0002'] = 'o'
db['post.0003'] = 'l'
db['zi.0001'] = 'k'
db['zi.0002'] = 'o'
db['zi.0003'] = 'l'

def query(prefix, **kw):
    it = db.get_iter(prefix, **kw)
    print(len(it))
    for i in it: print(i)

query('user', asc=1)
query('user.', asc=1)
query('user.', asc=0)

query('',)

def value_index(k,v):
    return v

newpairs = []
for key, value in db.get_iter('user'): # every key prefixed 'user'
    indexkey = value_index(key, value)
    if indexkey is not None:
        # create index entry, but don't insert into db just yet because
        # we don't want to break the iterator
        newpairs.append((
            'index.value_index.' + indexkey + '.' + key,
            key,
        ))

for k,v in newpairs: db.put(k,v) # now

query('',)
query('index.value_index.Alice.',)
