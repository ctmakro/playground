var {
  Engine,Render,World,
  Bodies,Constraint,Composites,
  Mouse,MouseConstraint,Common
} = Matter

// create an engine
var engine = Engine.create();

// create a renderer
var render = Render.create({
  element: document.getElementById('showArea'),
  engine,
});

// create two boxes and a ground
var cart = Bodies.rectangle(400, 200, 40, 20,{
  density:1,
  friction: 0,
  frictionStatic:0,
  frictionAir: 0,

});
var mass = Bodies.circle(400,100,20,{
  density:1,
  friction: 0,
  frictionStatic:0,
  frictionAir: 0,

  collisionFilter:{
    category:0x0001,
    mask:0x00000000,//just dont collide with anything
    group:0
  }
})

var ground = Bodies.rectangle(400, 340, 810, 10, {
  isStatic: true,
  friction: 0,
  frictionStatic:0,
  frictionAir: 0,
});

// add all of the bodies to the world
World.add(engine.world, [
  cart,
  mass,
  ground
]);

World.add(engine.world,Constraint.create({
  bodyA:mass,
  bodyB:cart,
  stiffness:1.9,
  length:200,//pixels
}))

var mc = MouseConstraint.create(engine,{
  element: render.canvas
})

World.add(engine.world,mc)

// run the engine
Engine.run(engine);

// run the renderer
Render.run(render);
