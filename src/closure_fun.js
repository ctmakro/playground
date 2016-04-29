/*
funniest code, ever
*/

this.funny = 'funny global';
var funny = 'funny global';

this.funny2 = 'funny2 global';

notfunny = 'notfunny global';
evenfunny = 'evenfunny global';

function looking(){
  console.log(this.funny);
  console.log(funny);
  console.log();
  console.log(this.funny2);
  console.log(funny2);
  console.log();
  console.log(notfunny);
  console.log(evenfunny);
  console.log();
  console.log(bad);
  console.log(worse);
  console.log(worst);

  console.log(gettingfunny);
}

function closing(){
  this.funny = 'funny closing';
  this.funny2 = 'funny2 closing';

  notfunny = 'notfunny closing';
  var evenfunny = 'evenfunny closing';
  looking();
}

var bad = 'badly'
closing();
var worse = 'worse'
gettingfunny = 'hitting error'
