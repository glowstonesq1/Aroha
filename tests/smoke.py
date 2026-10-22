"""End-to-end smoke test for Aroha.
Run:  pip install playwright && playwright install chromium
      python3 -m http.server 8080 --directory .  (from the project root, in another terminal)
      python3 tests/smoke.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8080/'
errors = []

def check(cond, msg):
    if not cond:
        errors.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 393, 'height': 852})
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.goto(URL)
    check(pg.evaluate('Aroha.selfTest()') == 'ok', 'selfTest: ' + str(pg.evaluate('Aroha.selfTest()')))
    pg.click('.skip')                                   # skip intro
    pg.wait_for_selector('text=Get started')
    pg.click('text=I already have an account')
    pg.fill('#lem', 'kaif@example.com'); pg.fill('#lpw', 'secret1')
    pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=Before we start')
    pg.click('[data-act=consent]')
    check(pg.inner_text('#cons-e') != '', 'consent requires ticks')
    pg.check('#c18'); pg.check('#cAgree'); pg.click('[data-act=consent]')
    pg.wait_for_selector('text=Step 1 of 5')
    pg.click('text=Stick to schedule'); pg.click('text=Save & Next')
    pg.click('text=Prefer to skip, thanks')
    pg.click('text=Save & Next'); pg.click('.opt[data-v=No]'); pg.click('text=Save & Next')
    pg.click('.opt[data-v="Prefer not to say"]'); pg.click('text=Save & Next')
    pg.click('.swipe'); pg.wait_for_selector('text=Health check-ins')
    check(pg.is_visible('text=Today\u2019s plan'), 'plan card shows for schedule goal')
    check(pg.is_visible('text=Your week'), 'week card shows')
    # log and browser back
    pg.click('text=Log your symptoms'); pg.click('text=Sweating'); pg.click('[data-act=saveLog]')
    pg.wait_for_selector('text=Health check-ins')
    check('checked in on 1' in pg.inner_text('.week'), 'week summary counts the log')
    pg.click('.nav >> text=Library'); pg.go_back(); pg.wait_for_selector('text=Health check-ins')
    check(pg.url.endswith('#home'), 'browser back returns home, got ' + pg.url)
    # SOS has crisis lines
    pg.click('.sos-pill'); pg.wait_for_selector('.sopt.danger')
    pg.keyboard.press('Escape')
    # app lock
    pg.click('[data-go=profile]'); pg.click('text=Account')
    pg.fill('#lk1', '1234'); pg.fill('#lk2', '1234'); pg.click('#lkOn button')
    pg.wait_for_selector('text=Turn off')
    pg.reload(); pg.click('.skip'); pg.wait_for_selector('text=Welcome back')
    pg.fill('#pinIn', '1111'); pg.wait_for_selector('text=That PIN is not right')
    pg.fill('#pinIn', '1234'); pg.wait_for_selector('h1:has-text("Account")')   # reopens where you left off
    # deep link
    pg.evaluate("location.hash='todos'")             # in-app hash change (PWA shortcut while open)
    pg.wait_for_selector('text=TO - DO\u2019S')
    pg.evaluate("location.hash='sos'"); pg.wait_for_selector('.sopt.danger')
    pg.keyboard.press('Escape')
    pg.goto(URL + '#todos'); pg.reload(); pg.click('.skip'); pg.fill('#pinIn', '1234')   # cold deep link
    pg.wait_for_selector('text=TO - DO\u2019S')
    b.close()

print('PASS' if not errors else 'FAIL\n' + '\n'.join(errors))
sys.exit(1 if errors else 0)
