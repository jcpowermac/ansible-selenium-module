#!/usr/bin/python

DOCUMENTATION = '''
---
module: selenium
short_description: foo
description: foo
version_added: null
author: Joseph Callen
requirements:
    - Xvfb
    - selenium
options:
notes:
    -
'''

try:
    from xvfbwrapper import Xvfb
    HAS_XVFB = True
except ImportError:
    HAS_XVFB = False

try:
    from selenium import webdriver
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

import atexit

def start_xvfb(module):
    try:
        xvfb = Xvfb(width=1280, height=720)
        xvfb.start()
        atexit.register(xvfb.stop)
    except:
        module.fail_json(msg="xvfb broke")

def start_selenium_driver(module):
    driver = webdriver.Firefox()
    # Lets make sure that firefox is closed at the exit of the module
    atexit.register(driver.close)

    driver.implicitly_wait(30)
    driver.get(module.params['url'])
    module.params['driver'] = driver

def login(module):
    driver = module.params['driver']
    username = driver.find_element_by_id( module.params['username_element_id'] )
    password = driver.find_element_by_id( module.params['password_element_id'] )

    username.send_keys(module.params['username'])
    password.send_keys(module.params['password'])
    password.submit()



def find_xpath(module):
    driver = module.params['driver']
    for href_element in driver.find_elements_by_xpath(module.params['xpath']):
        href = href_element.get_attribute('href')
        if module.params['click_link']:
            href_element.click()
            # Problem here is when is the download done?
        else:
            # Currently we are going to assume (might not be a good idea but for time)
            # that there is only one link with the xpath as provided
            module.exit_json(changed=False, url=href)


def create_argument_spec():

    argument_spec = dict()
    argument_spec.update(
        url=dict(required=True, type='str'),
        username=dict(required=True, aliases=['user', 'admin'], type='str'),
        password=dict(required=True, aliases=['pass', 'pwd'], type='str', no_log=True),
        username_element_id=dict(required=True, type='str'),
        password_element_id=dict(required=True, type='str'),
        xpath=dict(required=False, type='str'),
        click_link=dict(required=False, default=False, choices=BOOLEANS),
        time_to_download=dict(required=False, default=10, type='int'),
    )
    return argument_spec


def main():
    argument_spec = create_argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_SELENIUM:
        module.fail_json(msg="selenium is missing")
    if not HAS_XVFB:
        module.fail_json(msg="xvfb is missing")

    start_xvfb(module)
    start_selenium_driver(module)
    login(module)
    if module.params['xpath']:
        find_xpath(module)
    else:
        # Not an elegant solution but only download small files with this method.
        # Just going to sleep based on time_to_download
        time.sleep(module.params['time_to_download'])
	module.exit_json(changed=False, msg="Should have downloaded url: %s" % module.params['url'] )


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
