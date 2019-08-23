'''
a spike is a signal sent from one neuron to another.
the signal departs at a given time and arrives at a later time.
'''
class Spike:
    def __init__(s, orig, dest, time_depr, time_arvl):
        s.orig = orig
        s.dest = dest
        s.time_depr = time_depr
        s.time_arvl = time_arvl

    def __repr__(self):
        return 'spike from {}({:.2f}) to {}({:.2f})'.format(
            self.orig, self.time_depr,
            self.dest, self.time_arvl,
        )

'''
a neuron is a unit with its internal state known as voltage.
voltage will change when spikes come in and/or out.
voltage will change on itself over time according to a predetermined rule.
'''

e = 2.71828182845904590
tao = 0.2 # abitary. larger = slower decay

ncounter = 0
ndict = {}

def get_name_for_neuron(neuron):
    s = 'n'+str(ncounter)
    ncounter+=1
    ndict[s] = neuron
    return s

class Neuron:
    def __init__(s, targets, t, v, name):
        s.targets = targets
        s.t = t
        s.v = v

        if name is None:
            s.name = get_name_for_neuron(s)
        else:
            if name in ndict:
                raise 'name already used'
            else:
                s.name = name
                ndict[name] = s

    def __repr__(self):
        return 'Neuron "{}"'.format('' if self.name is None else self.name)

    # spikes for all downstream targets
    def generate_spikes(self, nowt):
        if self.targets is None:
            print(self, 'no target to send to')
            spikes = ()
        else:
            spikes = tuple((Spike(self, target, nowt, nowt + 0.1)
            for target in self.targets))
        return spikes

    # voltage function over time
    def vf(self, v0, t0, t1):
        assert t1 >= t0
        dt = t1 - t0

        # voltage decreases over time
        v1 = v0 * e ** (-dt / tao)
        return v1

    # voltage at given time
    def vt(self, t1):
        return self.vf(self.v, self.t, t1)

    def recv_spike(self, t):
        newt = t
        newv = self.vt(newt)

        # voltage increases when spikes hit
        newv += 0.5

        # send out spikes if voltage exceed a given threshold
        if newv > 0.7:
            spikes = self.generate_spikes(newt)

            # reset the neuron's voltage to half if spikes are sent.
            newv -= 0.5
        else:
            spikes = ()

        # set new state for the neuron.
        self.t = newt
        self.v = newv

        return spikes

def simulate(neurons, spikes, t_max=0, resolution=None, t_extend=0.3):

    neurons = tuple(neurons)
    q = list(spikes)
    q.sort(key=lambda s:s.time_arvl)

    t = 0

    histq = []
    histv = []

    samplecounter = 0

    def print_neuron_voltages_at_time(t):
        print('({:.2f}) '.format(t) + \
        ' '.join([
            '{}:{:.2f}V'.format(n.name,n.vt(t))
            for n in neurons
        ]))

    def log_neuron_voltages_at_time(t):
        histv.append((t, tuple((n.vt(t) for n in neurons))))

    print_neuron_voltages_at_time = log_neuron_voltages_at_time

    def incr_samplecounter_and_eval_until(f, t_end):
        nonlocal samplecounter
        while 1:
            sample_t = samplecounter * resolution
            if sample_t > t_end:
                break
            else:
                f(sample_t)
                samplecounter+=1

    while 1:
        if len(q)==0:
            # no more spikes to send from queue

            # simulate a bit more past the last spike.
            if resolution is not None:
                incr_samplecounter_and_eval_until(
                    print_neuron_voltages_at_time,
                    t + t_extend,
                )
            break

        else:
            # queue is not empty

            cs = curr_spike = q.pop(0)
            new_t = cs.time_arvl

            if resolution is not None:
                incr_samplecounter_and_eval_until(
                    print_neuron_voltages_at_time,
                    new_t,
                )

            print(cs)

            new_spikes = cs.dest.recv_spike(new_t) # may generate new spike(s)

            if new_spikes is None:
                pass
            else:
                for s in new_spikes: # add generated spike(s) into queue
                    q.append(s)
                q.sort(key=lambda s:s.time_arvl)

            histq.append(cs) # add current spike into history.

            if t_max != 0:
                if new_t >= t_max:
                    break

            t = new_t

    return histq, histv

def default_neuron(targets=(), name=None):
    return Neuron(targets=targets, t=0, v=0, name=name)

def default_spike(target, t):
    return Spike(orig=None, dest=target,
        time_arvl=t, time_depr=t)

dn = default_neuron
ds = default_spike

n2 = dn((), 'n2')
n3 = dn((), 'n3')
n1 = dn((n2,n3), 'n1')

neurons = (n1, n2, n3)
spikes = (
    ds(n1,0.1),
    ds(n1,0.2),
    ds(n1,0.8),
)

histq, histv = simulate(
    neurons=neurons,
    spikes=spikes,
    resolution=0.01,
)

def plot(neurons, histq, histv):
    assert len(histv)>0
    nneurons = len(neurons)

    rndict = {} # reverse neuron dictionary.
    # find index given identity of neuron.

    for i in range(nneurons):
        rndict[neurons[i]] = i

    import matplotlib

    from sys import platform as _platform
    if _platform == "darwin":
        # MAC OS X
        matplotlib.use('qt5Agg')
        # avoid using cocoa or TK backend, since they require using a framework build.
        # conda install pyqt

    from matplotlib import pyplot as plt

    xs = []
    ys = [[] for i in range(nneurons)]
    rowheight = .5

    def getycoord(i): return i * rowheight

    # voltage-time data processing
    for h in histv:
        xs.append(h[0])
        for i in range(nneurons):
            ys[i].append(h[1][i] + getycoord(i))
            # add an offset to each line

    fig, ax = plt.subplots()

    # voltage-time plot and label for the neurons
    for i in range(nneurons):
        ax.plot(xs, ys[i])
        ax.text(xs[0], ys[i][0],
            s = neurons[i].name,
            # size=50,
            bbox=dict(
                boxstyle="round",
                # ec=(1., 0.5, 0.5),
                fc=(1, 1, 1, 0.9),
            )
        )

    # count spikes to draw
    arrival_spikes = [[] for i in range(nneurons)]
    departure_spikes = [[] for i in range(nneurons)]

    for spike in histq:
        tarr = spike.time_arvl
        tdpr = spike.time_depr

        dest_i = rndict[spike.dest]
        arrival_spikes[dest_i].append(tarr)

        if spike.orig is not None: # pulse is between neurons
            orig_i = rndict[spike.orig]
            departure_spikes[orig_i].append(tdpr)

            # arrow between pair of spikes
            ax.arrow(
                x = tdpr,
                y = getycoord(orig_i + rowheight),
                dx = tarr-tdpr,
                dy = getycoord(dest_i) - getycoord(orig_i),
                width = 0.003,
                head_width = 0.03,
                head_length = 0.06,
                length_includes_head = True,
                color = (0.3,0.3,0,0.12),
                # linestyle = (0,(3,3)),
            )

    # now draw the spikes
    for i in range(nneurons):
        epd = {
            # 'positions' : departure_spikes[i],
            'orientation' : 'horizontal',
            'lineoffsets' : (i+.5) * rowheight,
            'linelengths' : rowheight,
            # 'colors' : (.1,.1,.8,.5),
            # 'linestyles' : 'dashed',
            # 'label' : 'pulse departure',
        }

        ax.eventplot(
            positions = arrival_spikes[i],
            colors = (.3,.3,.3,.3),
            # linestyles = 'dashed',
            linestyles = ((0,(3,3)),),
            label = 'pulse arrival' if i==0 else None,
            **epd,
        )
        ax.eventplot(
            positions = departure_spikes[i],
            colors = (1,.3,.3,.2),
            linestyles = 'solid',
            label = 'pulse departure' if i==0 else None,
            **epd,
        )


    ax.set_title('Neuron Voltages versus Time')
    ax.set_ylabel('Voltage')
    ax.set_xlabel('Time')

    ax.legend()
    plt.show()


# print(histq)
# print(histv)
plot(neurons, histq, histv)
