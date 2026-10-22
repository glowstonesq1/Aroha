# Aroha feature audit (v0.4.0)

**The job Aroha does:** help a young adult with generalised anxiety (1) get through a hard moment, (2) notice their own patterns, and (3) keep everyday life moving, without overwhelming them. Everything is on the device. There is no server.

Each feature was tested against three questions:

1. Does it serve one of those three jobs?
2. Is it honest? Does it work the way the screen says it does?
3. Could it make anxiety worse?

## Removed

| Feature | Why it goes |
|---|---|
| **Camera heart-rate check** (finger on the lens and flash) | Repeatedly checking your pulse is a known *safety behaviour* in panic and health anxiety: it keeps attention on body sensations and feeds the fear loop. A phone camera estimate is also unreliable, and a "Below/above resting range" warning from a noisy reading can trigger the attack it was meant to help with. Manual heart-rate entry goes too, for the same reason. |
| **Body temperature log** | Phones can't measure it, and fever has nothing to do with anxiety care. It was a health-dashboard habit, not a GAD tool. |
| **Login, sign-up, password, social sign-in buttons** | With no server there is no account. "I already have an account" on a new phone found nothing. The Google, Apple and Facebook buttons did nothing. Privacy on a shared phone is the app lock's job. Moving to a new phone is a backup file's job, and the welcome screen now offers "Restore from a backup". |
| **Onboarding questions about gender, age, height, weight, past therapy, medication** | Nothing in the app used the answers. Collecting health data you don't use goes against data minimisation (DPDP Act s.6, GDPR art. 5) and adds four screens before any help. |
| **"What makes Aroha unique" screen** | A marketing slide between the user and the app. The four pillars now live in About. |
| **Community feed, likes, follows, comments, chats** | Every post, comment and chat partner was sample content, and nobody ever replied. A person in crisis could message "Dr. Nilambari" and get silence. A real community needs moderation and a safeguarding path first (see README). Human connection stays through **Your people**: trusted contacts the SOS sheet can message in one tap. |
| **Videos tab in Safe box** | Videos were lost on every reload because localStorage can't hold them. |
| **Playlist and sample voice notes** | The playlist couldn't be created or edited, and the "recordings" were silent samples. |
| **Fullscreen audio player** | A native `<audio>` control does the same job, with accessibility built in. |
| **Mood tracker and sleep tracker printables** | They duplicated the calendar and the log in a second place, so data could disagree. |
| **"Chances of attack?" tile** | The title promised a prediction the app can't make. |
| **"Videos / Blogs / Articles" filter** | There were no videos; every item was a short read. |
| **Sample to-dos and sample contacts** ("Dinner with Mihika", "Ankit Y") | Someone else's life pre-filled into the user's to-do list and emergency list. |

## Changed

| Before | After | Why |
|---|---|---|
| Mood set: happy, sad, neutral, gloomy, excited | happy, calm, neutral, **anxious**, sad | An anxiety app had no way to log "anxious". Old entries map over: excited to happy, gloomy to sad. |
| Sleep in a separate printable tracker | "How did you sleep?" inside the daily log | One check-in, one place. The weekly summary now reports sleep. |
| Home opened with heart rate and temperature | Home opens with **"How are you right now?"**: one tap logs today's mood | The core loop is a 2-second check-in, not a vitals dashboard. |
| Insight tiles: log, physical health, chances of attack | Tiles for what helps now: **Breathe**, **Ground**, **Log** | Each tile does something. |
| Calendar hidden behind a date chip | **Journal** tab: month or year view coloured by mood, and recent entries you can reread | You could save notes but never read them back. |
| Nav: Home, Safe box, Library, To-dos, Community | Home, **Journal**, Safe box, Library, To-dos | Journal replaces the removed community. |
| Onboarding: 7 to 9 screens | Welcome, consent, name, goals, your people, ready | Fewer steps before help. Adding a trusted person early makes SOS useful from day one. |
| Hand-drawn stroke icons | Phosphor Icons (light weight, MIT) inlined as SVG | One consistent icon family. No third-party request, so the CSP stays `'self'`. |
| Profile, Edit profile, Logout | **You**: edit your name inline, then Your people, Privacy and data, Help, About, Legal | No account means no logout. |
| Library sections by type | Sections by need: **Calm now**, **Understand anxiety**, **Everyday life** | Find what helps by the situation you're in. A new read on sleep fills a real gap. |

## Kept as they were
Splash intro, consent with 18+ check, SOS sheet (breathing, 5-4-3-2-1 grounding, message a trusted person, region-aware crisis lines), crisis-language nudge, app lock, to-dos with step breakdown and carry-over, safe box memories and keepsake cards, voice notes (3-minute cap), weekly trends instead of streaks, backup, restore and delete-all, light and dark themes, PWA and offline.

## Data migration
`normalise()` reads v2 data:

- moods map to the new set;
- the old sleep tracker folds into logs;
- removed fields (heart rate, temperature, profile answers, account hash, community state) are dropped on the next save;
- sample memories and silent sample recordings are dropped.

Nothing the user created is lost except heart-rate and temperature readings, which are part of the removed features.
