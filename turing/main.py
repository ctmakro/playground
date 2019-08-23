import random

def r(n): return random.randint(0,n)
def mod8(n): return n%256

'''
each symbol on the tape is a byte (0-255).
blank symbol is 0.

machine state is a byte.
initial machine state is 0.

'''

class tape:
    def burn(self, verbose=False):
        while 1:
            self.step(generate_report=verbose)
            if self.energy<=0:
                break

        return self.offsprings

    def eval(self):
        pass

    def __init__(self, program, energy=2000):
        self.original_tape = program
        self.tape = [] + program # make copy

        self.left_extend = 0 # how far the tape is extended to the left.

        self.pointer = 0

        self.energy = energy
        self.state = 0

        self.output = []
        self.offsprings = []

        self.replicate_counter = 0

    def read_tape(self, idx):
        idx += self.left_extend

        while idx<0:
            self.tape.insert(0,0)
            self.left_extend+=1
            idx+=1

        while idx>=len(self.tape):
            self.tape.append(0)

        return self.tape[idx]

    def write_tape(self, idx, val):
        idx += self.left_extend
        self.tape[idx] = val

    def step(self, generate_report=False):
        old_pointer = self.pointer

        curr_symbol = self.read_tape(old_pointer)
        curr_state = self.state

        calculated = mod8(curr_symbol * curr_state + 47)

        # determine new state
        new_state = calculated

        # determine what symbol to write
        j=r(256)
        new_symbol = mod8(calculated*curr_state*37+(j if r(j)==0 else 0))

        # determine to keep current symbol or overwrite
        overwrite = 90 < calculated < 100

        # determine L or R
        direction = calculated < 127

        # write to output?
        wo = 1 < calculated < 20

        # terminate write to output?
        we = 30 < calculated < 40

        new_symbol = new_symbol if overwrite else curr_symbol
        self.write_tape(old_pointer, new_symbol)

        if wo:
            self.output.append(new_symbol)

        if we:
            self.offsprings.append(self.output)
            self.output = []

        dir_scalar = 1 if direction else -1
        new_pointer = self.pointer + dir_scalar

        self.pointer = new_pointer

        self.state = new_state
        self.energy -= 1

        if generate_report:
            report = \
            '#{:5d} st({:3d}) * sy({:3d}) = st({:3d}) wr({:3d}) #{:5d}({}) [{:5d}]'.format(
                old_pointer,
                curr_state,
                curr_symbol,
                new_state,
                new_symbol,
                new_pointer,
                "R" if direction else "L",
                self.energy,
            )
            print(report)

def fitness(t):
    return len([k for k in t if k%5==0])**2/len(t)

def sim():
    population = []

    for j in range(10000):

        print('iter',j)
        while len(population)<512:
            population.append(
                tape([r(256) for i in range(32)])
            )

        new_pop = []
        new_pop_offs = []

        npop = len(population)
        noff = 0

        for t in population:
            offsprings = t.burn()
            valid_offsprings = [o for o in offsprings if len(o)>3]

            noff+=len(valid_offsprings)
            # print(len(valid_offsprings), 'offs')

            sofff = 0

            for o in valid_offsprings:
                nt = tape(o)
                nt.replicate_counter = t.replicate_counter+1
                offf = fitness(nt.original_tape)
                new_pop_offs.append((offf, nt))
                sofff+=offf

            bt = tape(t.original_tape)
            bt.replicate_counter = t.replicate_counter

            # new_pop.append((fitness(t.original_tape) + sofff * 0.9, bt))
            new_pop.append((sofff, bt))

        new_pop = sorted(new_pop, key=lambda n:n[0])
        new_pop_offs = sorted(new_pop_offs, key=lambda n:n[0])

        print('eval pop {}, yielding {}, minp {} maxp {} mino {} maxo {}'.format(
        npop, noff,
        new_pop[0][0], new_pop[-1][0],
        new_pop_offs[0][0], new_pop_offs[-1][0],
        ))
        print(new_pop_offs[-1][1].replicate_counter,
        new_pop_offs[-1][1].original_tape,)

        population = [k[1] for k in new_pop_offs[-512:]]
        # print('lenpop',len(population))

        # population += [k[1] for k in new_pop[-(512-len(population))//2:]]
        # print('lenpop',len(population))

        print('avgrep', sum([k.replicate_counter for k in population])/len(population))


# t1 = tape([r(256) for i in range(128)])

# offs = t1.burn(verbose=True)

# print(offs)
sim()
