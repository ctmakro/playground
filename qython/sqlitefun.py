import sqlite3 as lite
import psycopg2 as pg

from hashsource import hashsource

def inc_char(char):
    return chr(ord(char)+1)

class CantonDB:
    def __init__(self, keypath_function=None, debug=False, *a, **kw):
        self.connect(*a, **kw)

        self.debug = debug

        if keypath_function is None:
            self.keypath_function = lambda k,v:(v,)
        else:
            self.keypath_function = keypath_function

        self.keypath_function_hash = hashsource(self.keypath_function)
        if debug:
            print(self.keypath_function_hash)

        self.init_table()
        self.update_all_index()

    def connect(self, *a, **kw):
        self.conn = lite.connect(*a, **kw)
        self.backend = 'sqlite'

    def generate_keypaths(self, key, value):
        return self.keypath_function(key, value)

    def init_table(self):
        self.query('create table if not exists kv(key text, value text, version text)')
        self.query('create unique index if not exists ik on kv(key)')
        self.query('create index if not exists ikver on kv(version)')

        self.query('create table if not exists ind(keypath text, key text)')
        self.query('create index if not exists ii0 on ind(keypath, key)')
        self.query('create index if not exists ii1 on ind(key)')

    def put(self, key, value):
        if self.backend=='sqlite':
            self.query('replace into kv values(?,?,?)',(key, value, None), commit=False)
        else:
            self.query('delete from kv where key=?',(key,), commit=False)
            self.query('insert into kv values(?,?,?)',(key, value, None), commit=False)
        self.update_index(key, value)

    def get(self, key):
        fetched = self.query('select value from kv where key=?',(key,))
        if len(fetched):
            return fetched[0][0]
        else:
            return None

    def delete(self, key):
        self.query('delete from kv where key=?',(key,), commit=False)
        self.query('delete from ind where key=?',(key,))

    def update_index(self, key, value, commit=True):
        new_keypaths = self.generate_keypaths(key, value)
        version = self.keypath_function_hash
        kpk = [(kp, key) for kp in new_keypaths]
        self.query('delete from ind where key=?',(key,), commit=False)
        self.query('insert into ind values(?,?)', kpk, many=True, commit=False)
        self.query('update kv set version=? where key=?',(version, key), commit=commit)

    def update_all_index(self):
        conn = self.conn
        debug = self.debug
        version = self.keypath_function_hash

        total = 0
        while 1:
            if debug:
                print('uai:', total)

            # cur = conn.cursor()
            kvs = self.query('select key,value from kv where version !=? limit 100', (version,))
            # kvs = cur.fetchall()
            if len(kvs) == 0:
                break
            else:
                total += len(kvs)
                for k,v in kvs:
                    self.update_index(k, v, commit=True)
                # conn.commit()

    def query(self, q, values=(), many=False, commit=True):
        conn = self.conn
        debug = self.debug
        query_is_select = 'select' in q
        if debug:
            print('sql>', q, values)
            if query_is_select:
                cur = conn.cursor()
                if self.backend == 'sqlite':
                    cur.execute('explain query plan '+q, values)
                else:
                    cur.execute('explain '+q, values)

                fetched = cur.fetchall()
                print('sql> (plan)', fetched)

        cur = conn.cursor()
        if many:
            cur.executemany(q, values)
        else:
            cur.execute(q, values)

        if query_is_select:
            fetched = cur.fetchall()
            if debug:
                print('sql<', fetched)
            return fetched
        else:
            if commit:
                conn.commit()

    def prefix(self, prefix, order='asc', limit=1000, offset=0, count=False):
        start = prefix
        end = prefix[:-1] + inc_char(prefix[-1])

        sort_order = 'ASC' if order.lower()=='asc' else 'DESC'

        query = 'select ' + ('count(*)' if count else '*') +\
        ' from kv where key>=? and key<? ' +\
        'order by key '+sort_order+' limit ? offset ?'

        if count:
            return self.query(query, (start, end, limit, offset))[0][0]
        else:
            return self.query(query, (start, end, limit, offset))

    def prefix_index(self, prefix, order='asc', limit=1000, offset=0, count=False):
        start = prefix
        end = prefix[:-1] + inc_char(prefix[-1])

        sort_order = 'ASC' if order.lower()=='asc' else 'DESC'

        if count:
            query = 'select count(*)' +\
            ' from ind where keypath>=? and keypath<? ' +\
            'order by keypath '+sort_order+' limit ? offset ?'
        else:
            query = 'select kv.key, kv.value' +\
            ' from ind inner join kv on kv.key=ind.key where keypath>=? and keypath<? ' +\
            'order by keypath '+sort_order+' limit ? offset ?'

        if count:
            return self.query(query, (start, end, limit, offset))[0][0]
        else:
            return self.query(query, (start, end, limit, offset))

    def reset(self):
        self.query('drop table kv')
        self.init_table()

    def __getitem__(self,key):
        return self.get(key)

    def __setitem__(self,key,value):
        return self.put(key,value)

    def __delitem__(self, key):
        return self.delete(key)

class CantonDBPG(CantonDB):
    def connect(self, *a, **kw):
        self.conn = pg.connect(*a, **kw)
        self.backend = 'pg'

    def query(self, q, *a, **kw):
        q = q.replace('?','%s')
        return super().query(q, *a, **kw)

import json

def o2j(o):
    return json.dumps(o, ensure_ascii=False)

def j2o(j):
    return json.loads(j)

if __name__ == '__main__':

    def kpf(key, value):
        o = j2o(value) # assume all json in db
        keypaths = []
        def add(s):keypaths.append(s)
        def attr(s):
            if s in o:
                return o[s]
            else:
                return None

        if 'type' in o:
            add('object/type/{}/'.format(attr('type')))

            if o['type'] == 'user':
                add('user/name/{}/'.format(attr('name')))
                add('user/t_reg/{}/'.format(attr('t_reg')))

        return keypaths

    # db = CantonDB(database='test.db', keypath_function=kpf, debug=True)
    db = CantonDBPG(keypath_function=kpf, debug=True,
        host='192.168.1.59',user='postgres', dbname='db')

    # db.reset()

    db.put('4g9u1',o2j({
        'type':'user',
        'name':'alice',
        'id':1,
        't_reg':1999,
    }))
    db.put('13121',o2j({
        'type':'user',
        'name':'bob',
        'id':2,
        't_reg':2015,
    }))
    db.put('411u1',o2j({
        'type':'user',
        'name':'charlie',
        'id':3,
        't_reg':1965,
    }))
    db.put('j8889',o2j({
        'type':'user',
        'name':'bobby',
        'id':4,
        't_reg':1965,
    }))

    print(j2o(db.get('411u1')))

    db.update_all_index()

    db.prefix_index('user/name/{}/'.format('bob'))
    db.prefix_index('user/t_reg/{}/'.format('1999'))
    db.prefix_index('user/t_reg/', order='desc')
    db.prefix_index('user/t_reg/', count=True)
    db.prefix_index('object/type/user/')

    # db.put('hello','world')
    # db.get('hello')
    # del db['hello']
    # db.get('hello')
    #
    # db['user.0001'] = 'Alice'
    # db['user.0002'] = 'Charlie'
    # db['user.0003'] = 'Bob'
    # db['user.'] = 'Test'
    # db['user'] = 'Test'
    # db['user0001'] = 'Test'
    # db['username.0001'] = 'Alice'
    # db['username.0002'] = 'Charlie'
    # db['username.0003'] = 'Bob'
    #
    # db['post.0001'] = 'k'
    # db['post.0002'] = 'o'
    # db['post.0003'] = 'l'
    # db['zi.0001'] = 'c'
    # db['zi.0001'] = 'k'
    # db['zi.0009'] = 'k'
    # del db['zi.0009']
    # db['zi.0002'] = 'o'
    # db['zi.0003'] = 'l'
    #
    # db.prefix('user')
    # db.prefix('user', order='DESC')
    # db.prefix('user', order='DESC', count=True)
    # db.prefix('user', count=True)
    # db.prefix('user', order='DESC', limit=2, offset=1)
    #
    # db.prefix_index('k')
    # db.prefix_index('c')
    # db.prefix_index('k', count=True)
    #
    # db.update_all_index()
