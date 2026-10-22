"""End-to-end smoke test for Aroha.
Run:  pip install playwright && playwright install chromium
      python3 -m http.server 8080 --directory .  (from the project root, in another terminal)
      python3 tests/smoke.py
Set CHROMIUM_PATH to use an already-installed Chromium instead of Playwright's download.
"""
import os, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8080/'
errors = []

def check(cond, msg):
    if not cond:
        errors.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None)
    pg = b.new_page(viewport={'width': 393, 'height': 852})
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.on('request', lambda r: errors.append('third-party request: ' + r.url) if not r.url.startswith(URL) and not r.url.startswith('data:') else None)
    def skip():                                         # returning users get a short intro that may already be gone
        try: pg.click('.skip', timeout=1500)
        except Exception: pass
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
    pg.reload(); skip(); pg.wait_for_selector('text=Welcome back')
    pg.fill('#pinIn', '1111'); pg.wait_for_selector('text=That PIN is not right')
    pg.fill('#pinIn', '1234'); pg.wait_for_selector('h1:has-text("Account")')   # reopens where you left off
    # deep link
    pg.evaluate("location.hash='todos'")             # in-app hash change (PWA shortcut while open)
    pg.wait_for_selector('text=TO - DO\u2019S')
    pg.evaluate("location.hash='sos'"); pg.wait_for_selector('.sopt.danger')
    pg.keyboard.press('Escape')
    pg.goto(URL + '#todos'); pg.reload(); skip(); pg.fill('#pinIn', '1234')   # cold deep link
    pg.wait_for_selector('text=TO - DO\u2019S')
    # SOS shortcut skips the intro: the sheet must be up long before the 2 s short intro would end
    pg.goto(URL + '#sos'); pg.reload(); pg.wait_for_selector('.sopt.danger', timeout=1200)
    check(not pg.is_visible('.splash'), 'SOS deep link skips the splash')
    pg.keyboard.press('Escape'); pg.fill('#pinIn', '1234'); pg.wait_for_selector('text=Health check-ins')
    # crisis words in a note open helplines instead of leaving the page
    pg.click('text=Log your symptoms'); pg.fill('#notes', 'honestly I dont want to live like this'); pg.click('[data-act=saveLog]')
    pg.wait_for_selector('text=You don\u2019t have to carry this alone'); pg.keyboard.press('Escape')
    # a media item that overflows storage is dropped, and later saves still work
    pg.evaluate("location.hash='safebox'"); pg.wait_for_selector('text=New Memories??')
    pg.set_input_files('#fileImg', files=[{'name': 'big.png', 'mimeType': 'image/png', 'buffer': open(os.path.join(os.path.dirname(__file__), '..', 'og-image.png'), 'rb').read()}])
    pg.wait_for_selector('text=Memory added')
    pg.evaluate("(()=>{let i=0;for(const n of [1e5,1e4,1e3,100,10]){const s='x'.repeat(n);try{for(;i<1e5;i++)localStorage.setItem('aroha.fill'+i,s)}catch(e){}}})()")   # fill storage to the last byte
    n_before = pg.evaluate("JSON.parse(localStorage.getItem('aroha.v1')).photos.length")
    pg.set_input_files('#fileImg', files=[{'name': 'big2.png', 'mimeType': 'image/png', 'buffer': open(os.path.join(os.path.dirname(__file__), '..', 'og-image.png'), 'rb').read()}])
    pg.wait_for_selector('text=Not enough space')
    check(pg.evaluate("JSON.parse(localStorage.getItem('aroha.v1')).photos.length") == n_before, 'overflowing photo rolled back')
    pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('aroha.fill')).forEach(k=>localStorage.removeItem(k))")
    # logout is real: someone else's email or a wrong password does not reopen the logs
    pg.evaluate("location.hash='profile'"); pg.click('text=Logout'); pg.wait_for_selector('#lem')
    pg.fill('#lem', 'someone@else.com'); pg.fill('#lpw', 'secret1'); pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=don\u2019t match')
    pg.fill('#lem', 'kaif@example.com'); pg.fill('#lpw', 'wrong-pass'); pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=don\u2019t match')
    pg.click('text=Sign - up'); check(pg.input_value('#snm') == '' and pg.input_value('#sem') == '', 'signup does not show the previous user')
    pg.fill('#snm', 'X'); pg.fill('#sem', 'x@y.com'); pg.fill('#spw', 'secret2'); pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=already has an Aroha account')
    pg.go_back(); pg.wait_for_selector('#lem')
    pg.fill('#lem', 'KAIF@example.com'); pg.fill('#lpw', 'secret1'); pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=Health check-ins')        # email is case-insensitive; password just proved, so no PIN prompt
    check('checked in on 1' in pg.inner_text('.week'), 'data still there after logging back in')
    b.close()

print('PASS' if not errors else 'FAIL\n' + '\n'.join(errors))
sys.exit(1 if errors else 0)
