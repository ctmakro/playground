require 'torch'
require 'gnuplot'
require 'nn'
require 'image'
require 'paths'

function nn:GracefulSequential()
  local net = nn.Sequential()

  function net:conv(i,o,N)
    self:add(nn.SpatialConvolution(i,o,N,N))
  end

  function net:maxpool()
    self:add(nn.SpatialMaxPooling(2,2))
  end

  function net:avgpool()
    self:add(nn.SpatialAveragePooling(2,2))
  end

  function net:fc(i,o)
    self:add(nn.Linear(i,o))
  end

  function net:relu()
    self:add(nn.ReLU())
  end

  function net:logsoftmax()
    self:add(nn.LogSoftMax())
  end

  function net:flat(i)
    self:add(nn.View(i))
  end

  return net
end

function loadcifar()
  if (not paths.filep("cifar10torchsmall.zip")) then
    os.execute('wget -c https://s3.amazonaws.com/torch7/data/cifar10torchsmall.zip')
    os.execute('unzip cifar10torchsmall.zip')
  end
  local trainset = torch.load('cifar10-train.t7')
  local testset = torch.load('cifar10-test.t7')
  local classes = {'airplane', 'automobile', 'bird', 'cat',
  'deer', 'dog', 'frog', 'horse', 'ship', 'truck'}

  print'CIFAR-10 loaded'

  return trainset,testset,classes
end

function imd(im,z)
  image.display(im,z)
end

function setIndexer(obj,f)
  setmetatable(obj, {__index = f})
end

function tick()
  timer = timer or torch.Timer()
  lasttick = lasttick or 0
  local now = timer:time().real

  local interval = now-lasttick
  lasttick = now

  return now,interval
end

function bragTick()
  local now, interval = tick()
  print(string.format('batch: %f s tot: %f s',interval,now))
end

trainset,testset,classes = loadcifar()

-- trainset should have size() and [i] indexer
-- methods
setIndexer(trainset,function(obj, idx)
  return {obj.data[idx], obj.label[idx]}
  --[1] for sample, [2] for label
end)

function trainset:size()
  return self.data:size(1) --sizeof first dimension
end
---

trainset.data = trainset.data:double()
testset.data = testset.data:double()
-- convert the data from a ByteTensor to a DoubleTensor.

function normalize(trainset)
  --calc mean and stddev on each channel
  local mean,stdv = {},{}
  for i=1,3 do
    mean[i]=trainset.data[{{},{i},{},{}}]:mean()
    trainset.data[{{},{i},{},{}}]:add(-mean[i])

    stdv[i]=trainset.data[{{},{i},{},{}}]:std()
    trainset.data[{{},{i},{},{}}]:div(stdv[i])

    print('on channel '..i..':')
    print('mean '..mean[i]..' stdv '..stdv[i])

  end
  return mean,stdv
end

function applyNormalization(set,mean,stdv)
  for i=1,3 do
    set.data[{{},{i},{},{}}]:add(-mean[i])
    set.data[{{},{i},{},{}}]:div(stdv[i])
  end
end

mean,stdv = normalize(trainset)
applyNormalization(testset,mean,stdv)

imd(trainset.data[100])

net = nn.GracefulSequential()

net:conv(3,64,5) --30
net:maxpool() --15
net:relu()

net:conv(64,64,5) --13
net:relu()
net:avgpool() --6.5

net:conv(64,64,5)
net:relu()
net:avgpool()
--net:pool(2)

net:flat(1024) --400
net:fc(1024,10)
net:logsoftmax()

print(net)

--throw '123'

criterion=nn.ClassNLLCriterion() -- class neg. log-like.

---GPUize---
function gpuize()
  require 'cunn'
  net = net:cuda()
  criterion = criterion:cuda()
  trainset.data = trainset.data:cuda()
  trainset.label = trainset.label:cuda()
end
---GPUize---

trainer = nn.StochasticGradient(net, criterion)
trainer.learningRate = 0.002
trainer.maxIteration = 1
-- just do 5 epochs of training.

function runtest()
  local correct = 0
  for i=1,10000 do
    local groundtruth = testset.label[i]
    local prediction = net:forward(testset.data[i])
    local confidences, indices = torch.sort(prediction, true)  -- true means sort in descending order
    if groundtruth == indices[1] then
      correct = correct + 1
    end
  end
  return correct
end

net.modules[1].weight:div(16)
net.modules[4].weight:div(16)

function train_till_degrade()
  local last_acc = 0
  local epochs = 0

  plotarr = {}

  tick()
  while 1 do

    trainer:train(trainset)
    epochs = epochs+1
    if epochs>10 then break end
    bragTick()

    print('epoch '..epochs..' ended, testing............................')

    local acc=runtest()
    print('accuracy on testset: '.. acc/10000)
    plotarr[epochs]=1-(acc/10000)

    gnuplot.figure(1)
    gnuplot.title('error rate on testset')
    gnuplot.plot(torch.Tensor(plotarr))

    local w = net.modules[1].weight
    imd({image=w:view(w:size(1)*w:size(2),w:size(3),w:size(4)),zoom=3,padding=1})

    if acc<last_acc*0.9 then
      print('accuracy is decreasing too much, stop training')
      break
    else
      last_acc = math.max(last_acc,acc)
    end

  end
end
----
train_till_degrade()

require('trepl')()
