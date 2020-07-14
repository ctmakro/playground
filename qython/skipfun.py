class Node:
    pass
def dummy(key=None):
    n = Node()
    n.key = key
    n.value = None
    n.forwards = []
    # n.height=0
    return n

inf = float('inf')
minf = float('-inf')

import random

class SkipList:
    def __init__(self):
        self.head = dummy()
        self.tail = dummy(inf)
        self.head.forwards.append(self.tail)
        self.levels = 1 # number of levels at start

        self.updates = [None]*self.levels # reuse

    def generate_height(self):
        h = 0
        while random.randrange(2)==0:
            h += 1
            if h == self.levels:
                break
        return h

    def insert(self, key, value):

        updates = self.updates
        x = self.head

        # for each level from top to bottom
        for level in reversed(range(self.levels)):
            # go right if key > rightnode.key
            while key > x.forwards[level].key:
                x = x.forwards[level]
            # key <= rightnode.key
            # leftnodes[level] = leftnode
            updates[level] = x

        # x = rightnode
        x = x.forwards[0]

        # if key == rightnode.key
        if x.key == key:
            # that's it
            x.value = value

        # key < rightnode.key
        else:
            new_height = self.generate_height()

            # increase level of entire skiplist if necessary
            if new_height > self.levels - 1:
                for i in range(self.levels, new_height + 1):
                    updates.append(self.head)
                    self.head.forwards.append(self.tail)
                self.levels = new_height+1

            node = dummy(key)
            node.value = value
            # node.height = new_height

            # make links in every level <= height
            for i in range(new_height+1):
                node.forwards.append(updates[i].forwards[i])
                updates[i].forwards[i] = node

    def traverse(self, limit=100):
        n = self.head
        while limit>0:
            print('k:{} v:{} h:{}'.format(n.key, n.value, len(n.forwards)))
            limit -= 1
            if n.forwards:
                n=n.forwards[0]
            else:
                break

skl = SkipList()

for i in range(50000):
    skl.insert(random.randrange(100000000),random.randrange(100))

skl.traverse(20)
