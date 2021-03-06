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

def _do_group_manager_request(command, data):
    # Disable unsecure connection warning.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f'{YODA_PORTAL}/group-manager/{command}'

    cookies = {'csrf_yoda': csrf, 'yoda_session': session}
    data['csrf_yoda'] = csrf

    res = requests.post(url, data=data, cookies=cookies, verify=False, timeout=10)

    body = res.json()

    return (res.status_code, body)

def _do_api_request(command, data):
    # Disable unsecure connection warning.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f'{YODA_PORTAL}/api/{command}'
    print(url)
    files = {'csrf_yoda': (None, csrf), 'data': (None, json.dumps(data))}
    cookies = {'csrf_yoda': csrf, 'yoda_session': session}

    res = requests.post(url, files=files, cookies=cookies, verify=False, timeout=10)
    body = res.json()

    return (res.status_code, body)


csrf, session = _login(YODA_USER, YODA_PW)
print(csrf, session)

s, b = _do_api_request('group_data', {})
print(s, b)

username = 'xyz123'
role = 'manager'
group = {'group_name': 'datamanager-aimms3',
         'group_category': 'aimms3',
         'group_subcategory': 'dm',
         'group_description': 'created by web api'}
s, b = _do_group_manager_request('group-create', group)
print(s, b)

# does this trigger an invitation email for external users?
s, b = _do_group_manager_request('user-create', {'user_name': username, 'group_name': group['group_name']})
print(s, b)

s, b = _do_group_manager_request('user-update', {'user_name': username, 'group_name': group['group_name'], 'new_role': role})
print(s, b)
