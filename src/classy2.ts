var print = console.log

var makeClass = (function classmaker(){
  // make subclasses of this class
  function make_subclass(){
    return make(this)
  }

  // check if __init__ exists in class
  function check_init(self,args){
    if(self.__init__){ // if __init__ method exists
      self.__init__.apply(self,args)
    }else{
      throw '__init__() missing. did you miss the keyword "new"?'
    }
  }

  // bind a new method to class
  function bind_method(name,f){
    if(typeof name === 'string'){
      this.prototype[name]=f
    }else{
      Object.assign(this.prototype,name)
      // for(var key in name){
      //   this.prototype[key] = name[key]
      // }
    }
    return this
  }

  var make = function(parentclass){
    var newclass = function(){
      check_init(this,arguments)
    }

    if(parentclass&&parentclass.prototype){
      // inherit all methods using prototype chaining, if parent exists
      newclass.prototype.__proto__ = parentclass.prototype
      newclass.super = parentclass
    }

    newclass.methods = newclass.prototype
    newclass.subClass = make_subclass
    newclass.bind = bind_method
    return newclass
  }
  return make
})()


var Animal = makeClass()

Animal.methods.__init__ = function(sound){
  this.sound = sound||'[null]'
  this.legs = 4
}

Animal.methods.talk = function(){
  print('i say '+this.sound + ' have ' + this.legs + ' legs')
}

var Sheep = Animal.subClass()

Sheep.methods.__init__ = function(){
  Sheep.super.methods.__init__('baa')
}

Sheep.methods.yell = function(){
  this.sound += '!'
  this.talk()
}


var ani = new Animal()
var ani2 = new Animal('meow')

ani.talk()
ani2.legs = 5
ani2.talk()

var sh = new Sheep()

sh.talk()
sh.yell()
sh.yell()

var Cow = Sheep.subClass()

// Cow.methods.__init__ = function(){
//   Cow.super.methods.__init__()
//   this.sound = 'moo'
// }

Cow.bind('__init__',function(){
  Cow.super.methods.__init__()
  this.sound='moo'
})
.bind('eat',function(){
  print('eating grass')
})

var c = new Cow()

c.talk()
c.yell()
c.eat()

var make = (f)=>{
  return {
    new:f
  }
}

var make = (()=>{
  function tie(inst,mobj){
    inst.__proto__ = mobj
  }
  function gen(mobj){
    var self = {} // data
    tie(self,mobj)
    return self
  }
  var make = method_obj=>{
    function initiate(){
      var self = gen(method_obj)
      self.__init__.apply(this,[self].concat(Array.from(arguments)))
      return self
    }
    initiate.make = new_method_obj=>{
      new_method_obj.super = method_obj
      tie(new_method_obj,method_obj)
      return make(new_method_obj)
    }
    return initiate
  }
  return make
})()


var Animal = make({
  __init__(self,sound){
    self.sound = sound||'[null]'
    self.legs = 4
  },
  talk(self){
    print(`i say ${self.sound} have ${self.legs} legs`)
  }
})

// var Animal = make(sound=>{
//   var self = {}
//   self.sound = sound||'[null]'
//   self.legs = 4
//   self.__proto__.talk = ()=>{
//     print(`i say ${self.sound} have ${self.legs} legs`)
//   }
//   return self
// })

var ani = Animal()
ani.talk(ani)

var Sheep = Animal.make({
  __init__(self){
    self.super.__init__(self)
    self.sound = 'baa'
  },
  yell(self){
    self.sound += '!'
    self.talk(self)
  }
})
// var Sheep = make(function(){
//   var self = Animal.new()
//   self.sound = 'baa'
//   self.yell = ()=>{
//     self.sound+='!'
//     self.talk()
//   }
//   return self
// })
//
var sh = Sheep()

sh.talk(sh)
sh.yell(sh)

ani.talk(sh)

print('---')

var make = (()=>{
  var make = function(populator){
    var c = function(){this.__init__(this,arguments)}
    if(typeof populator==='function')populator(c.prototype)
    else c.prototype = populator
    return c
  }
  var make_new = function(new_populator){
    var nc = make(new_populator)
    nc.prototype.__proto__ = this.prototype
    nc.prototype.super = this.prototype
    return nc
  }
  Function.prototype.make = make_new
  return make
})()

var Animal = make(p=>{
  p.__init__ = function(){
    this.sound = 'naaa'
    this.legs = 4
  }
  p.talk = function(){
    print(`i say ${this.sound} have ${this.legs} legs`)
  }
})


var inst = new Animal()
inst.talk()

var Cat = Animal.make(p=>{
  p.__init__ = function(){
    this.super.__init__()
    this.sound = 'meow'
  }
})

var cat = new Cat()
cat.talk()

var Sheep = Cat.make({
  __init__(){
    this.sound = 'baa'
  },
  yell(){
    this.sound+='!'
    this.talk()
  }
})

var sh = new Sheep()
sh.yell()
sh.yell()

switch(1){
  case 1:{
    print('hello')
  }
}

var ano = function(){
  this.bi = 'a'
}
ano.prototype.say = function(){
  this.bi += 'b'
  print(this.bi)
}
var bno = new ano()

print(bno.bi)
bno.say()
