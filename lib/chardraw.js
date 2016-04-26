var str = ['asdfb', 'apdfb', 'acatbull', 'amanagement boss', 'abanana'];
console.log(str);
var coexisted = {};
function intersect(set1, set2) {
  var resultset = {};
  for (i in set1) {
    if (set2[i])
      resultset[i] = true;
  }
  return resultset;
}
function toset(arr) {
  var resultset = {};
  for (i in arr) {
    resultset[arr[i]] = 1;
  }
  console.log(resultset);
  return resultset;
}
function stringtoset(str) {
  return toset(str.split(''));
}
var baseset = {};
function aggr(set1, set2) {
  var resultset = {};
  for (i in set1) {
    resultset[i] = set1[i];
  }
  for (i in set2) {
    if (resultset[i])
      resultset[i] += set2[i];
    else {
      resultset[i] = set2[i];
    }
  }
  return resultset;
}
var str = ['eite2m', 'rit12maa', 'hite2m11101100'];
function commonhead(str1, str2) {
  var len = Math.min(str1.length, str2.length);
  var k;
  var str = '';
  for (var i = 0; i < len; i++) {
    if (str1.charAt(i) != str2.charAt(i)) {
      str += '-';
    } else {
      str += str1.charAt(i);
    }
  }
  return str;
}
var basestr = str[0];
for (i in str) {
  basestr = commonhead(basestr, str[i]);
}
console.log(basestr);
