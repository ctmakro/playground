var xsize = 640
var ysize = 480

var svg = d3.select('#showArea')
.append('svg').attr('width',xsize).attr('height',ysize)

//math coord.
var xscale = d3.scaleLinear().domain([0,1]).range([xsize/2,xsize/2+ysize/4])
var yscale = d3.scaleLinear().domain([0,1]).range([ysize/2,ysize/4])

var clamp = (val,min,max)=>Math.max(Math.min(val,max),min)

function appendStyleSheet(s){
  d3.select('body').append('style').text(s)
}

class Shape{
  constructor(options){
    let op = options
    this.identifier = 'id'+Math.floor((Math.random()*65536*65536)).toString()

    this.tagname = op.tagname
    this.updateAttr = op.updateAttr
    this.initAttr = op.initAttr

    if(op.stylesheet)appendStyleSheet(op.stylesheet)
  }

  repaint(dataSet){
    //to read the code below, you should be familiar with d3.js
    let shapes = svg.selectAll('#'+this.identifier).data(dataSet)

    //update
    this.updateAttr(shapes)

    //newcomer
    this.updateAttr(this.initAttr(shapes.enter().append(this.tagname).attr('id',this.identifier)))

    //out
    shapes.exit().remove()
  }
}

function times(num,fun){while(num--)fun(num);}
var random = (magnitude,center)=>Math.random()*(magnitude||1)-(center||0)


var circle = new Shape({
  tagname:'circle',

  initAttr:function(s){
    return s.attr('r',20)
    .attr('class','greencircle')
  },

  updateAttr:function(s){
    return s
    .attr('cx',d=>xscale(d.x))
    .attr('cy',d=>yscale(d.y))
  },

  stylesheet:`
  .greencircle {
    fill:pink;
    stroke:black;
    stroke-width:2;
  }`
})

var box = new Shape({
  tagname:'rect',
  initAttr:s=>{
    return s.attr('class','box')
  },
  updateAttr:s=>{
    return s
    .attr('x',d=>xscale(d.x)-d.w/2)
    .attr('y',d=>yscale(d.y)-d.h/2)
    .attr('width',d=>d.w)
    .attr('height',d=>d.h)

  },
  stylesheet:`
  .box {
    fill:gray;
    stroke:black;
  }
  `
})

var line = new Shape({
  tagname:'line',
  initAttr:s=>{
    return s.attr('class','line')
  },
  updateAttr:s=>{
    return s
    .attr('x1',d=>xscale(d.x1))
    .attr('y1',d=>yscale(d.y1))
    .attr('x2',d=>xscale(d.x2))
    .attr('y2',d=>yscale(d.y2))
  },
  stylesheet:`
  .line {
    stroke:rgba(0,0,0,0.5);
    stroke-width:2;
  }
  `
})

var text = new Shape({
  tagname:'text',
  initAttr:s=>{
    return s.attr('class','sometext')
  },
  updateAttr:s=>{
    return s
    .attr('x',d=>d.x).attr('y',d=>d.y)
    .text(d=>d.text)
  },
  stylesheet:`
  .sometext{
    font-size:16;
  }`
})

var pi = Math.PI

//degrees of freedom
var cart = {
  f : 0,// N
  pos: new vector(0,1),
  v: new vector(0,0),
  a: new vector(0,0)
}

var stick = {
  l : 1, // meter
}

var mass = {
  m : 0.5, // kg
  f : new vector(0,0), // N
  pos: new vector(0,1),
  v: new vector(0,0),
  a: new vector(0,0)
}

var pushforce = 0 // human push
var pfc = 3 // push force multiplier

var bound = {
  left : -1,
  right : 1
}

class vector {
  constructor(x,y){
    this.x=x
    this.y=y
  }

  add(v){
    return new vector(this.x+v.x,this.y+v.y)
  }

  mul(a){
    return new vector(this.x*a,this.y*a)
  }

  inv(){
    return new vector(-this.x,-this.y)
  }

  norm(){
    return Math.sqrt(this.x*this.x+this.y*this.y)
  }
}

var cos = Math.cos
var abs = Math.abs
var sin = Math.sin
var g = 9.8
var fc = 0.01 //air friction coeff.
var fc2 = 0.01 //road friction coeff.

function simulation_step(stepsize){
  function airfriction(speed,coeff){
    return speed.inv()
    .mul(speed.norm())
    .mul(coeff)
  }


  //cart force
  var cart_fric = airfriction(cart.v,fc2)
  var cart_push = new vector(pushforce*pfc,0) //push force

  //mass force
  mass.fy = mass.m * g


  mass.f = // total force on mass (angular)
  - mass.m * g * cos(stick.theta) // by gravity
  - ( - fric + pushforce*pfc ) * sin (stick.theta)
  - abs(stick.omega) * stick.omega * fc // by air friction

  stick.a = mass.f / mass.m / stick.l // angular acceleration



  cart.a = cart.f / cart.m

  cart.v += cart.a * stepsize

  //collision detection
  if(cart.x>bound.right){
    cart.x = bound.right - (cart.x-bound.right);cart.v=-cart.v
  }

  if(cart.x<bound.left){
    cart.x = bound.left - (cart.x-bound.left);cart.v=-cart.v
  }

  cart.x += cart.v * stepsize

  stick.omega += stick.a * stepsize
  stick.theta += stick.omega * stepsize

  mass.x = cart.x + stick.l * cos(stick.theta)
  mass.y = cart.y + stick.l * sin(stick.theta)
}

var log = ''

var repaint = function(){
  simulation_step(0.02)

  text.repaint([{
    x:30,y:30,text:log
  }])

  line.repaint([{
    x1:mass.x,y1:mass.y,
    x2:cart.x,y2:cart.y,
  },{
    x1:-1,y1:0,
    x2:1,y2:0,
  }])

  box.repaint([{
    x:cart.x,y:cart.y,w:40,h:20
  }])

  circle.repaint([{
    x:mass.x,y:mass.y
  }])
}

var di = d3.interval(repaint,20)

d3.select('body').on('keydown',function(){
  switch(d3.event.keyCode){
    case 37:
    pushforce=-1;break;
    case 39:
    pushforce=1;break;
  }
})
d3.select('body').on('keyup',function(){
  switch(d3.event.keyCode){
    case 37:
    case 39:
    pushforce=0;break;
  }
})
