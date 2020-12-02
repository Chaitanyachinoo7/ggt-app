import ujson

with open("permissions_list.json") as f:
    data = ujson.load(f)

permissions = data['permissions']
roles = data['roles']

_permissions = []

for p in permissions:
    _permissions.append({
        "value": p,
        "description": "Roles with {} permission will allow to access API end point which contains {} in scopes.".format(
            p, p)
    })
body = {
    "permissions": _permissions
}
with open('temp.permissions.json', 'w') as outfile:
    ujson.dump(body, outfile)

st = ''

for p in permissions:
    _p = p.upper()
    st = "{} {} = '{}' \n".format(st, _p, p)

with open('temp.txt', 'w') as outfile:
    outfile.write(st)
