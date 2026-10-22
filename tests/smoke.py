"""End-to-end smoke test for Aroha.
Run:  pip install playwright && playwright install chromium
      python3 -m http.server 8080 --directory .  (from the project root, in another terminal)
      python3 tests/smoke.py
Set CHROMIUM_PATH to use an already-installed Chromium instead of Playwright's download.
"""
import json, os, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8080/'
OG = open(os.path.join(os.path.dirname(__file__), '..', 'og-image.png'), 'rb').read()
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
    pg.click('.skip')
    # onboarding: welcome, consent, name, goals, people, ready
    pg.click('text=Get started'); pg.wait_for_selector('text=Before we start')
    pg.click('[data-act=consent]'); check(pg.inner_text('#cons-e') != '', 'consent requires ticks')
    pg.check('#c18'); pg.check('#cAgree'); pg.click('[data-act=consent]')
    pg.wait_for_selector('text=Step 1 of 3'); pg.fill('#obn', 'Kaif'); pg.click('.ob-foot .btn')
    pg.click('text=Stick to schedule'); pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=Step 3 of 3'); pg.fill('#acn', 'Mihika'); pg.fill('#acp', '12'); pg.click('.ob-foot .btn')
    pg.wait_for_selector('text=Enter a valid phone number')
    pg.fill('#acp', '+91 98200 12345'); pg.click('.ob-foot .btn')
    pg.click('.swipe'); pg.wait_for_selector('text=Hi Kaif, how are you right now?')
    check(pg.is_visible('text=Today’s plan'), 'plan card shows for schedule goal')
    check(pg.is_visible('text=Send a check-in text'), 'onboarding contact reaches Your people')
    check(pg.locator('text=Heart Rate').count() == 0 and pg.locator('text=Body temp').count() == 0, 'vitals are gone')
    # one-tap check-in, then a full log, then reread it in the journal
    pg.click('.checkin [data-m=anxious]'); pg.wait_for_selector('text=Noted for today.')
    check('checked in on 1' in pg.inner_text('.week') and 'anxious' in pg.inner_text('.week'), 'week summary counts the check-in')
    pg.click('.three [data-go=log]'); check(pg.get_attribute('.logsheet [data-m=anxious]', 'aria-checked') == 'true', 'log opens with today’s mood')
    pg.click('text=6-7h'); pg.click('#symchips >> text=Sweating'); pg.fill('#notes', 'Exam tomorrow, breathing helped.'); pg.click('[data-act=saveLog]')
    pg.wait_for_selector('text=Open today\u2019s log')                      # back where the log was opened from
    pg.click('.nav >> text=Journal'); pg.wait_for_selector('text=Recent entries')
    check('slept 6-7h' in pg.inner_text('.entries') and 'Sweating' in pg.inner_text('.entries'), 'journal shows the entry')
    pg.click('.nav >> text=Library'); pg.go_back(); pg.wait_for_selector('text=Recent entries')
    check(pg.url.endswith('#journal'), 'browser back returns to journal, got ' + pg.url)
    # SOS: tools, trusted person, crisis lines
    pg.click('.nav >> text=Home'); pg.click('.sos-pill'); pg.wait_for_selector('.sopt.danger')
    check(pg.is_visible('text=Message Mihika'), 'SOS offers the trusted person')
    pg.click('.sheet [data-act=breathe]'); pg.wait_for_selector('text=Round 1 of 5'); pg.keyboard.press('Escape')
    # app lock
    pg.click('[data-go=profile]'); pg.click('text=Privacy & data')
    pg.fill('#lk1', '1234'); pg.fill('#lk2', '1234'); pg.click('#lkOn button')
    pg.wait_for_selector('text=Turn off')
    pg.reload(); skip(); pg.wait_for_selector('text=Welcome back')
    pg.fill('#pinIn', '1111'); pg.wait_for_selector('text=That PIN is not right')
    pg.fill('#pinIn', '1234'); pg.wait_for_selector('h1:has-text("Privacy & data")')   # reopens where you left off
    # deep links
    pg.evaluate("location.hash='todos'"); pg.wait_for_selector('text=TO - DO’S')
    pg.evaluate("location.hash='sos'"); pg.wait_for_selector('.sopt.danger'); pg.keyboard.press('Escape')
    pg.goto(URL + '#todos'); pg.reload(); skip(); pg.fill('#pinIn', '1234'); pg.wait_for_selector('text=TO - DO’S')
    pg.goto(URL + '#sos'); pg.reload(); pg.wait_for_selector('.sopt.danger', timeout=1200)   # skips the intro, works while locked
    check(not pg.is_visible('.splash'), 'SOS deep link skips the splash')
    pg.keyboard.press('Escape'); pg.fill('#pinIn', '1234'); pg.wait_for_selector('text=right now?')
    # crisis words in a note open helplines instead of leaving the page
    pg.click('.three [data-go=log]'); pg.fill('#notes', 'honestly I dont want to live like this'); pg.click('[data-act=saveLog]')
    pg.wait_for_selector('text=You don’t have to carry this alone'); pg.keyboard.press('Escape')
    # safe box: keepsake card, photo, and storage overflow rolls back
    pg.click('.nav >> text=Safe box'); pg.fill('#gIn', 'Sunset at Marine Drive with Mihika'); pg.click('text=Keep it')
    pg.wait_for_selector('.mcard:has-text("Marine Drive")')
    pg.set_input_files('#fileImg', files=[{'name': 'trip.png', 'mimeType': 'image/png', 'buffer': OG}]); pg.wait_for_selector('text=Memory added')
    pg.evaluate("(()=>{let i=0;for(const n of [1e5,1e4,1e3,100,10]){const s='x'.repeat(n);try{for(;i<1e5;i++)localStorage.setItem('aroha.fill'+i,s)}catch(e){}}})()")
    n_before = pg.evaluate("JSON.parse(localStorage.getItem('aroha.v1')).photos.length")
    pg.set_input_files('#fileImg', files=[{'name': 'trip2.png', 'mimeType': 'image/png', 'buffer': OG}]); pg.wait_for_selector('text=Not enough space')
    check(pg.evaluate("JSON.parse(localStorage.getItem('aroha.v1')).photos.length") == n_before, 'overflowing photo rolled back')
    pg.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('aroha.fill')).forEach(k=>localStorage.removeItem(k))")
    pg.click('text=Voice notes'); pg.wait_for_selector('text=Record a voice note')
    # restore a v0.2 backup on a fresh device: moods map, sleep tracker folds in, removed features drop
    pg.evaluate("localStorage.clear()"); pg.goto(URL); pg.reload(); skip(); pg.wait_for_selector('text=Restore from a backup')
    old = {'v': 2, 'loggedIn': True, 'onboarded': True, 'consentAt': 1, 'user': {'name': 'Ria', 'email': 'r@x.com'}, 'hr': [{'bpm': 80, 'at': 1}],
           'logs': {'2026-10-01': {'mood': 'gloomy', 'symptoms': ['Trembling'], 'notes': 'rough day', 'at': 1}}, 'sleep': {'2026-10-01': '<5h'},
           'photos': [{'id': 's1', 'kind': 'art', 'art': 'wing', 'title': "Manali 24'"}], 'contacts': [{'id': 'c1', 'name': 'Ankit Y', 'phone': ''}]}
    pg.set_input_files('#fileJson', files=[{'name': 'aroha-backup.json', 'mimeType': 'application/json', 'buffer': json.dumps(old).encode()}])
    pg.wait_for_selector('text=Hi Ria, how are you right now?')
    pg.click('.nav >> text=Journal'); pg.wait_for_selector('text=Recent entries')
    entries = pg.inner_text('.entries')
    check('Sad' in entries and 'slept <5h' in entries and 'rough day' in entries, 'v0.2 log migrated: ' + entries)
    check('hr' not in pg.evaluate("JSON.parse(localStorage.getItem('aroha.v1'))"), 'heart rate dropped on migration')
    b.close()

print('PASS' if not errors else 'FAIL\n' + '\n'.join(errors))
sys.exit(1 if errors else 0)
