
var print = console.log
var program =
`
_
__
= x 2
= x
__+ 3 2
___
print x
while
__> x 0
__= x
____- x 1
__
iif
__> x 2
__- x 1
__+ x
____* 5 x`.replace(/_/g,' ')

// misc

var cond = function(){
  var arr = arguments
  for(var i=0;i<arr.length;i+=2){
    if(arr[i+1]!==undefined){if(arr[i]){return arr[i+1]}}
    else{return arr[i]}
  }
}
var range = i=>{var a=[];for(var j=0;j<i;j++)a.push(j);return a}
var last = (arr,s)=>arr[arr.length-1-(s||0)]
var first = arr=>arr[0]

print(cond(
  false,'1f',
  true,'2f',
  '3f'
))

print(program)

// node making
var makenode = function(type,parent,sy){
  if(type=='symbol'){
    var n = {type,parent,symbol:sy}
    parent.children.push(n)
    return n

  }else if(type=='list'){
    var n = {type,parent,children:[]}
    if(parent){parent.children.push(n)}
    return n

  }else{
    throw 'unsupported node type'
  }
}
var sy_node = (p,s)=>makenode('symbol',p,s)
var li_node = (p)=>makenode('list',p)

// state machinery
var parsing_statemachine = function(){
  // state reset
  var reset = ()=>{
    rootnode = li_node(null)
    currnode = rootnode
    acc = []
    sy_start()
    in_stack = []
    in_count = 0
    in_start()

    state = 'linestart'
  }

  // node switching state machine
  var rootnode = li_node(null)
  var currnode = rootnode

  // debug accumulator
  var acc = []
  var ain = n=>acc.push(n)

  // symbol parsing state machine
  var symbol_cache = '' // characters of symbol
  var sy_start = ()=>{symbol_cache=''}
  var sy_in = c=>{symbol_cache+=c}
  var sy_end = ()=>{
    var n = sy_node(currnode,symbol_cache)
    ain(n)
  }

  // indent parsing state machine
  var in_stack = []
  var in_count = 0

  var in_start = ()=>{in_count=0}
  var in_in = ()=>{in_count++}
  var in_end = ()=>{in_set(in_count)}

  // upon receiving EOS
  var str_end=()=>{
    in_set(0) // indent set to 0

    // no more code, no open brackets
    acc.pop()
    rootnode.children.pop()
  }

  // stack growth chart
  //      ()
  //   [ = x 2 (0)
  // ][ = x  (0)
  // [ + 3 2 (0,2)
  //
  // ]] [ prn x (0)
  // ] [ whi (0)
  // [ > x 0 (0,2)
  // ][ = x (0,2)
  // [ - x 1 (0,2,4)
  // end: ]]] ()

  // indentation controlled node switching
  var in_set = (i)=>{
    ain('indent '+i.toString()) // debug

    if(i>last(in_stack)||in_stack.length==0){ // more indentation
      in_stack.push(i)
    }else{ // less or equal
      list_end()
      while(i<last(in_stack)){ // while less
        in_stack.pop()
        list_end()
      }
      if(i>last(in_stack)){throw 'indentation imbalance'}
    }
    list_start()

    ain('stack:'+in_stack.toString()) // debug
  }

  // actual node switching routine
  var list_start = ()=>{
    currnode = li_node(currnode)
    ain('[') // debug
  }
  var list_end = ()=>{
    currnode = currnode.parent
    ain(']') // debug
  }

  // input character categorization
  var there = (c,str)=>(str.indexOf(c)>=0) // include
  var eq = str=> c=>c===str // equal

  var symbol = c=>
  ('a'<=c && c<='z') || ('A'<=c && c<='Z')||
  ('0'<=c && c<='9') || there(c,'.<>?=_-+*/')

  var space = eq(' ')
  var endl = eq('\n')
  var eos = eq('\0')

  // the categorizer
  var cat = c=>cond(
    symbol(c),'symbol',
    space(c),'space',
    endl(c),'newline',
    eos(c),'eos',
    'invalid'
  )

  // initial state
  var state = 'linestart'

  // mapping (parser_state, character_category) to corresponding_actions
  var statemap = {}
  // map registrator
  var reg = statename=>{
    var statenames = (typeof statename=='string')?[statename]:statename;
    var r = (charcat,handler)=>{
      statenames.map(sn=>{
        statemap[sn] = statemap[sn]||{}
        statemap[sn][charcat] = handler
      })
      return r
    }
    return r
  }

  // all the actions and state transitions

  reg('linestart') // at start of line
  ('symbol',c=>{state='symbol';in_start();in_end();sy_start();sy_in(c)})
  ('space',c=>{state='indenting';in_start();in_in()})

  reg('indenting') // during indentation of line
  ('symbol',c=>{state='symbol';in_end();sy_start();sy_in(c)})
  ('space',c=>{state='indenting';in_in()})

  reg('symbol') // during symbol
  ('symbol',c=>{sy_in(c)})
  ('space',c=>{sy_end();state='spacing'})
  ('newline',c=>{sy_end();state='linestart'})

  reg('spacing') // during spaces between symbol
  ('symbol',c=>{state='symbol';sy_start();sy_in(c)})
  ('space',c=>{state='spacing'})

  reg(['linestart','spacing','indenting'])
  ('newline',c=>{state='linestart'})
  ('eos',c=>{str_end();state='eos'})

  reg(['symbol'])
  ('eos',c=>{sy_end();str_end();state='eos'})

  var error = str=>{throw 'parse error: '+str}

  function eat(c){
    var s = statemap[state]
    if(s){ // if state exists
      var h = s[cat(c)]
      if(h){ //if handler exists
        h(c);//print('parse:',state,cat(c))
      }else{
        error(`handler not found for '${c}' of category: ${cat(c)} on state ${state}`)
      }
    }else{
      error(`unexpected state: ${state}`)
    }
  }

  function show_acc(){print(acc)}
  function show_state_map(){print(statemap)}

  function get_tree(){
    if((state=='eos')&&(in_stack.length==1)){
      return rootnode
    }else{
      throw 'parsing not completed'
    }
  }

  function parse(str){ // success or failure
    reset()
    for(var i=0;i<str.length;i++){
      eat(str[i])
    }
    eat('\0')
    return get_tree()
  }

  return {
    parse,
    show_acc,
    show_state_map,
  }
}

var psm = parsing_statemachine()

function traverse(node,f,depth){
  depth=depth||0
  f(node,depth)
  if(node.children){
    node.children.map(leaf=>{
      traverse(leaf,f,depth+1)
    })
  }
}

function parse (str){
  var tree = psm.parse(str)

  traverse(tree,(node,depth)=>{
    print(
      range(depth*4).map(x=>(x>(depth-1)*4)?'-':' ').join(''),
      node.type,
      node.symbol?node.symbol:''
    )
  })
}

var value_parsers = [
  function trynum(str){
    var accepted = ''
    var dot = false
    for(var i=0;i<str.length;i++){
      var c = str[i];
      if('0'<c && c<'9'){
        accepted+=c
      }else if(c=='.'&&dot==false){
        accepted+=c
        dot = true
      }else{
        return null
      }
    }
    return Number(accepted)
  },
  function trybool(str){
    if(str==='true')return true
    if(str==='false')return false
    return null
  },
]

// determine value for symbol node
function value(synode){
  var str = synode.symbol
  for(f of value_parsers){
    var res = f(str)
    if(res!==undefined){
      return res
    }
  }
  return synode
}


// variable map
var red = (f,r) => l => l.reduce(f,r||0)

// input l : list which elements were evaluated
var vmap = {
  '+':red((a,b)=>a+b),
  '-':l=>l[0]+red((a,b)=>a-b)(l.slice(1)),
  '*':red((a,b)=>a*b,1),
  '/':l=>l[0]/red((a,b)=>a*b,1),

  '=':l=>{vmap[l[0]] = l[1]},

  // while:l=>{while()}

  print:l=>print.apply(null,l),

}

function eval(node){ // non-root node
  if(node.children){

  }

}

parse(program)
