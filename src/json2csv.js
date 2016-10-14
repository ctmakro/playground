var res = require('./xsf_details.json')


var f = ''

for(i in res[0])
{f+=i+','}
f+='\n'

for(i in res){
  for(k in res[i]){
    f+=(res[i][k]||"").toString()+','
  }
  f+='\n'
}

console.log(f);

require('fs').writeFileSync('res.csv',f)
