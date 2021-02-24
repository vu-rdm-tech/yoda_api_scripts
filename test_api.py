import requests, json
import urllib3

from config import YODA_PORTAL, YODA_API_ROOT, YODA_PW, YODA_USER


# flow might be better:
# - ask username/password on CLI
# - get API key

def _login(user, password):
    """Login portal and retrieve CSRF and session cookies."""
    # Disable unsecure connection warning.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "{}/user/login".format(YODA_PORTAL)

    client = requests.session()

    # Retrieve the CSRF token first
    csrf = client.get(url, verify=False).cookies['csrf_yoda']

    # Login as user.
    login_data = dict(csrf_yoda=csrf, username=user, password=password, next='/home')
    client.post(url, data=login_data, headers=dict(Referer=url), verify=False)
    client.close()

    # Return CSRF and session cookies.
    return client.cookies['csrf_yoda'], client.cookies['yoda_session']


def _do_api_request(command, data):
    # Disable unsecure connection warning.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f'{YODA_PORTAL}{YODA_API_ROOT}/{command}'
    files = {'csrf_yoda': (None, csrf), 'data': (None, json.dumps(data))}
    cookies = {'csrf_yoda': csrf, 'yoda_session': session}

    res = requests.post(url, files=files, cookies=cookies, verify=False, timeout=10)

    body = res.json()

    return (res.status_code, body)


csrf, session = _login(YODA_USER, YODA_PW)
print(csrf, session)

s, b = _do_api_request('group_data', {})
print(s, b)

group = {'group_name': 'datamanager-aimms',
         'category': 'aimms',
         'subcategory': 'dm',
         'description': 'created by web api',
         'data_classification': 'restricted'}
s, b = _do_api_request('group_create', group)
print(s, b)
