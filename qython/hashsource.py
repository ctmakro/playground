import inspect, hashlib

def hashsource(f):
    source = inspect.getsource(f)
    h = hashlib.md5(source.encode('utf-8'))
    return h.hexdigest()[:8]

if __name__ == '__main__':
    def remedy():
        return haha

    print(hashsource(remedy))
