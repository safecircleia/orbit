#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Static checks for Orbit's release config. Run: python3 scripts/check_orbit_config.py"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECKS = []


def check(fn):
  CHECKS.append(fn)
  return fn


def text(path):
  return (ROOT / path).read_text()


def pref_value(name):
  pattern = re.compile(r'^- name: ' + re.escape(name) + r'\n  value: (.+)$', re.M)
  for yaml_file in (ROOT / 'prefs').rglob('*.yaml'):
    match = pattern.search(yaml_file.read_text())
    if match:
      return match.group(1).strip()
  return None


@check
def fullscreen_warning_not_suppressed():
  assert 'full-screen-api.warning' not in text('prefs/firefox/fullscreen.yaml'), \
      'fullscreen warning overrides still present'


@check
def hardening_prefs():
  expected = {
      'dom.security.https_only_mode': 'true',
      'browser.contentblocking.category': "'strict'",
      'privacy.fingerprintingProtection': 'true',
      'network.trr.mode': '2',
      'network.trr.uri': "'https://security.cloudflare-dns.com/dns-query'",
  }
  for name, value in expected.items():
    assert pref_value(name) == value, f'{name}: {pref_value(name)!r} != {value!r}'


@check
def resist_fingerprinting_untouched():
  assert pref_value('privacy.resistFingerprinting') is None


def patch_added_file(patch_path, file_path):
  section = text(patch_path).split(f'+++ b/{file_path}\n', 1)[1].split('\ndiff --git', 1)[0]
  lines = [line[1:] for line in section.splitlines()[1:] if line.startswith('+')]
  return '\n'.join(lines)


@check
def policies_json_valid_and_complete():
  import json
  body = patch_added_file(
      'src/browser/app/distribution/policies.patch', 'browser/app/distribution/policies.json')
  policies = json.loads(body)['policies']
  assert policies['BlockAboutConfig'] is True
  assert policies['Extensions']['Locked'] == ['uBlock0@raymondhill.net']
  engines = policies['SearchEngines']
  default = next(e for e in engines['Add'] if e['Name'] == engines['Default'])
  assert 'kp=1' in default['URLTemplate'], 'default engine must enforce safe search'
  assert '{searchTerms}' in default['URLTemplate']
  assert 'FINAL_TARGET_FILES.distribution' in text('src/browser/app/distribution/policies.patch')


ONBOARDING_PATCH = 'src/browser/components/aboutwelcome/orbit-onboarding.patch'


@check
def onboarding_enabled_and_first_run_points_at_it():
  assert pref_value('browser.aboutwelcome.enabled') is None, 'aboutwelcome is still disabled'
  urls = text('src/browser/themes/shared/branding/branding-welcome-urls.patch')
  assert urls.count('+pref("startup.homepage_welcome_url", "about:welcome");') == 2
  assert urls.count('+pref("startup.homepage_welcome_url.additional", "");') == 2


@check
def onboarding_screens_and_targeting():
  patch = text(ONBOARDING_PATCH)
  for needle in ('id: "ORBIT_WELCOME"', 'https://safecircle.tech/privacy',
                 '"AW_EASY_SETUP"', '"AW_IMPORT_SETTINGS_EMBEDDED"', '"AW_THEME_PICKER"'):
    assert needle in patch, f'missing {needle}'
  assert 'secondary_button_top' in patch, 'sign-in/backup buttons must be stripped'
  assert 'AW_THEME_PICKER' in patch and 'targeting' in patch, 'targeting must be preserved'


if __name__ == '__main__':
  failed = 0
  for fn in CHECKS:
    try:
      fn()
      print(f'ok   {fn.__name__}')
    except Exception as error:
      failed += 1
      print(f'FAIL {fn.__name__}: {type(error).__name__}: {error}')
  sys.exit(1 if failed else 0)
