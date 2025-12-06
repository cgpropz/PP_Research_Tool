# PrizePicks Autofill via Playwright

This folder contains a headless (or headed) automation to:
- Login once to PrizePicks and persist the session
- Reuse the saved session to open the app, select NBA, and add your picks

## Prereqs
- Node.js 18+
- macOS zsh shell (commands below)

## Install
```zsh
cd automation
npm install
npm run install:pw
```

## 1) Login once and save session
Runs a visible browser, you sign in, then it saves cookies/localStorage to `automation/storage-state.json` for reuse.
```zsh
cd automation
npm run login
```
If you need to relogin later, delete `automation/storage-state.json` and rerun the login step.

## 2) Autofill picks
You can provide your slip in two ways:

- Using the dashboard's share hash (`cgpp`):
  ```zsh
  cd automation
  CGPP="<paste-your-cgpp-base64>" npm run autofill:cgpp
  ```

- Using a local file (JSON):
  Create `automation/slip.json`:
  ```json
  {
    "version": 1,
    "items": [
      { "name": "LeBron James", "prop": "Points", "side": "Over" },
      { "name": "Nikola Jokic", "prop": "Rebounds", "side": "Under" }
    ]
  }
  ```
  Then run:
  ```zsh
  cd automation
  npm run autofill -- --slip ./slip.json
  ```

### Debug (headed mode)
Add `--headful` to watch it run with UI:
```zsh
cd automation
npm run autofill -- --slip ./slip.json --headful
```

## Notes
- The script selects the NBA/Basketball tab and defaults missing `side` to Over.
- If the homepage shows, it clicks "Pick Now" or "Players" to enter the picks UI.
- Selectors are resilient but UIs change—open an issue if anything needs tuning.
