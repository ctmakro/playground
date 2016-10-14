
var layer = (function(){
  'use strict';

  var layerObject = {}

  class layer{
    constructor(key,collection){
      this._key=key;
      this._collection=collection;
    }

    get key(){
      return this._key
    }
  }

  layerObject.layer = layer

  class post extends layer{
    constructor(key){
      super(key,'posts')
    }

    foo(){
      console.log(this._key,this._collection);
    }
  }

  layerObject.post = post

  return layerObject
})()

var post = layer.post
var k = new post(3)

k.foo()
