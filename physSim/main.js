var svg = d3.select('#showArea')
.append('svg').attr('width',640).attr('height',480)

function times(num,fun){
  while(num--)fun(num);
}
var random = (magnitude,center)=>Math.random()*(magnitude||1)-(center||0)

var somePoints = []
times(100,function(){
  somePoints.push({x:random(100),y:random(100),vx:random(1,0.5),vy:random(1,0.5)})
})

var circleManager = (function(){
  var cm = {}
  cm.identifier = 'id'+Math.floor((Math.random()*65536*65536)).toString()
  cm.tagname = 'circle'
  cm.updateAttr = function(s){
    return s.attr('cx',d=>d.x).attr('cy',d=>d.y)
  }

  cm.initAttr = function(s){
    return s.attr('r',2)
      .style('fill','lightgreen').style('stroke','green')
  }

  cm.repaint = function(dataSet){
    var circles = svg.selectAll('#'+cm.identifier).data(dataSet)

    //update
    cm.updateAttr(circles)

    //newcomer
    cm.updateAttr(cm.initAttr(circles.enter().append(cm.tagname).attr('id',cm.identifier)))

    //out
    circles.exit().remove()
  }

  return cm
})()

var step = function(scale){
  scale = scale||1
  for(i in somePoints){
    var p = somePoints[i]
    p.x+=p.vx*scale
    p.y+=p.vy*scale
  }
}

var repaint = function(){
  step(1)
  circleManager.repaint(somePoints)
}

repaint()

d3.interval(repaint,100)
