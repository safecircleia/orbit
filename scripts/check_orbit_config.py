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
  """Raw YAML value of a pref across prefs/**/*.yaml; None if absent; fails on duplicates."""
  pattern = re.compile(r'^- name: ' + re.escape(name) + r'\n  value: (.+)$', re.M)
  values = [match.group(1).strip()
            for yaml_file in (ROOT / 'prefs').rglob('*.yaml')
            for match in pattern.finditer(yaml_file.read_text())]
  assert len(values) <= 1, f'{name} is defined {len(values)} times in prefs/'
  return values[0] if values else None


@check
def fullscreen_warning_not_suppressed():
  for name in ('full-screen-api.warning.delay', 'full-screen-api.warning.timeout'):
    assert pref_value(name) is None, f'{name} override still present'


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
  assert 'const { secondary_button_top, ...rest } = content;' in patch, \
      'sign-in/backup buttons must be stripped'
  assert 'targeting: override?.targeting ?? targeting' in patch, 'targeting must be preserved'
  assert 'id === "AW_THEME_PICKER"' in patch, 'only the theme picker drops its targeting'


@check
def onboarding_reused_screens_still_exist_upstream():
  engine_file = ROOT / 'engine/browser/components/aboutwelcome/modules/AboutWelcomeDefaults.sys.mjs'
  if not engine_file.exists():
    return 'skipped: no engine/'
  upstream = engine_file.read_text()
  for screen_id in ('AW_EASY_SETUP', 'AW_IMPORT_SETTINGS_EMBEDDED', 'AW_THEME_PICKER'):
    assert f'id: "{screen_id}",' in upstream, f'{screen_id} no longer defined upstream'
  assert 'secondary_button_top:' in upstream, 'secondary_button_top was renamed upstream'


@check
def onboarding_default_browser_screen_has_no_checkbox_tile():
  patch = text(ONBOARDING_PATCH)
  assert 'Make Orbit your default' in patch
  assert 'tiles: undefined' in patch, 'multi-select tile overlaps the text in the center layout'
  assert 'type: "SET_DEFAULT_BROWSER"' in patch
  assert '!isDefaultBrowser' in patch, 'screen must be skipped when Orbit is already the default'
  assert "'browser.shell.checkDefaultBrowser'|preferenceValue" in patch


@check
def onboarding_defers_to_os_default_browser_prompt():
  assert '!${SET_DEFAULT_OS_PROMPT_ENABLED}' in text(ONBOARDING_PATCH), \
      'macOS/Windows show an OS prompt on first newtab; the screen must not ask twice'


@check
def policies_are_packaged():
  patch = text('src/browser/app/distribution/policies.patch')
  assert '+++ b/browser/installer/package-manifest.in' in patch, 'distribution/ is only packaged for BUILT_BY_MOZILLA'
  assert '-#if defined(BUILT_BY_MOZILLA)' in patch


@check
def release_metadata():
  import json
  surfer = json.loads(text('surfer.json'))
  assert surfer['brands']['beta']['release']['displayVersion'] == '0.2b'
  assert surfer['version']['version'] == '157.0'
  notes = json.loads(text('src/release-notes/stable.json'))
  assert notes[0]['version'] == '0.2b', f"latest release note is {notes[0]['version']}"
  assert 'Firefox 157' in json.dumps(notes[0])


@check
def prefs_readme_is_orbit():
  readme = text('prefs/README.md')
  assert 'Zen' not in readme and 'zen/' not in readme


if __name__ == '__main__':
  failed = 0
  for fn in CHECKS:
    try:
      note = fn()
      print(f'ok   {fn.__name__}' + (f' ({note})' if note else ''))
    except Exception as error:
      failed += 1
      print(f'FAIL {fn.__name__}: {type(error).__name__}: {error}')
  sys.exit(1 if failed else 0)
