var print = console.log

var example_instructions = [
  'stor dest value', // move value to DEST
  'mov dest from', // move 1 byte from addr in FROM to addr in DEST
  'add dest from1 from2', // add value of FROM1 and FROM2, store result in DEST
  'mul dest from1 from2', // same
  'jnz dest from', // jump to DEST if value of FROM is not zero
  'not dest from', // bit-not value of FROM, store result in DEST
]

// memory initialization
var memory = new Uint8Array(256)
var mem = memory

for(var i=0;i<mem.length;i++){
  mem[i]=255;
}

var name_inst_map = {}
var pi = name_inst_map

var code_inst_map = {}
var cim = code_inst_map

var instcounter = 0
function reg(instname, len, func){
  var instobj = {
    procedure:func,
    code:instcounter,
    length:len,
  }

  pi[instname] = instobj
  cim[instobj.code] = instobj

  print(`reg ${instcounter} "${instname}"`)
  instcounter++
}

reg('set',2, function(dest,value){
  mem[dest] = value
  print(`write ${value} into [${dest}]`)
})

reg('mov',2, function(dest,from){
  mem[mem[dest]] = mem[mem[from]]
  print(`move [[${from}]] into [[${dest}]]`)
})

function arith(opname, func){
  reg(opname, 3, function(dest,from1,from2){
    mem[dest] = func(mem[from1] , mem[from2]) % 256
    print(`${opname} [${from1}] and [${from2}] into [${dest}]`)
  })
}

arith('add',(a,b)=>a+b)
arith('mul',(a,b)=>a*b)
arith('sub',(a,b)=>a-b)
arith('div',(a,b)=>Math.floor(a/b))

reg('jnz',2,function(dest,from){
  if(mem[from]!==0)pc = dest
})

var pad=function(str, len){
  while(str.length<len){
    str = ' '+str
  }
  return str
}

var print_memory = function(){
  for(var i=0;i<32||mem[i]!==255;i++){
    print(`[${pad(i.toString(),3)}]  ${mem[i]}`)
  }
}

function parse_inst_line(line){
  var arr = line.split(' ')
  var instname = arr.shift()
  var inst = pi[instname]
  if(inst === undefined)throw new Error('unknown instruction');

  if(arr.length!==inst.length)
  throw new Error(
    `length of args for "${instname}" incorrect (${arr.length} instead of ${inst.length})`
  );
  arr = arr.map(i=>parseInt(i))
  arr.unshift(inst.code)

  return arr
}

// inst.procedure.apply(this, arr)

// compile text into bytes
function compile(program){
  return program.split('\n')
  .map(l=>l.split(';')[0])
  .map(l=>l.trim())
  .filter(l=>l.length>0)
  .map(parse_inst_line)
  .reduce((a,b)=>a.concat(b),[])
}

function byte2inst(b){
  var inst = cim[b]
  if(inst===undefined) throw new Error('unknown instruction byte');
  return inst
}

var pc = 0

function loadbyte(){
  return mem[pc++]
}

function run(program){
  var compiled = compile(program)
  print(compiled)

  // load the program into memory
  for(var i=0;i<compiled.length;i++){
    mem[15+i] = compiled[i]
  }

  // set pc
  pc = 15

  while(1){
    var b = loadbyte()
    if(b===255){
      print(`program end met at ${pc-1}`)
      break
    }

    var inst = byte2inst(b)
    var args=[]
    for(var i=0;i<inst.length;i++){
      args.push(loadbyte())
    }
    inst.procedure.apply(this,args)
  }

  print_memory()
}

run(
  `
  set 0 0
  set 1 2
  set 2 3

  set 5 4
  set 6 1

  mul 2 1 2 ;[2] = [1]*[2]
  sub 5 5 6 ;[5] = [5]-[6]

  jnz 30 5 ;goto [30] if [5]!=0
  `
)
