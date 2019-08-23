var print = console.log;
var makeClass = (function classmaker() {
    // make subclasses of this class
    function make_subclass() {
        return make(this);
    }
    // check if __init__ exists
    function check_init(self) {
        if (self.__init__) {
            self.__init__.apply(self, arguments);
        }
        else {
            throw '__init__() missing. did you miss the keyword "new"?';
        }
    }
    var make = function (parentclass) {
        var newclass = function () {
            check_init(this);
        };
        if (parentclass && parentclass.prototype) {
            // inherit all methods using prototype chaining, if parent exists
            newclass.prototype.__proto__ = parentclass.prototype;
            newclass.super = parentclass;
        }
        newclass.methods = newclass.prototype;
        newclass.subClass = make_subclass;
        return newclass;
    };
    return make;
})();
var Animal = makeClass();
Animal.methods.__init__ = function (sound) {
    this.sound = sound || '[null]';
    this.legs = 4;
};
Animal.methods.talk = function () {
    print('i say ' + this.sound + ' have ' + this.legs + ' legs');
};
var Sheep = Animal.subClass();
Sheep.methods.__init__ = function () {
    Sheep.super.methods.__init__('baa');
};
Sheep.methods.yell = function () {
    this.sound += '!';
    this.talk();
};
var ani = new Animal();
var ani2 = new Animal('meow');
ani.talk();
ani2.legs = 5;
ani2.talk();
var sh = new Sheep();
sh.talk();
sh.yell();
sh.yell();
var Cow = Sheep.subClass();
Cow.methods.__init__ = function () {
    Cow.super.methods.__init__();
    this.sound = 'moo';
};
var c = new Cow();
c.talk();
c.yell();
