import requests
import json
# Login


def authorize(schema):
    auth_endpoint = requests.get('https://auth.deezer.com/login/anonymous?jo=p')
    auth = auth_endpoint.json()["jwt"]

    headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {auth}"}
    # print(rq)

    z = requests.post('https://pipe.deezer.com/api', data=json.dumps(schema), headers=headers)
    return z.json()
