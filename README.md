# LCARS for T3 Code

A Star Trek: The Next Generation–style (LCARS) theme for [T3 Code](https://github.com/pingdotgg/t3code), with optional ship sounds for Claude Code.

The theme draws an LCARS frame around the app, runs a starfield that goes to warp while Claude works, and fades in hail, yellow alert and red alert when a thread needs you.

![LCARS theme while a thread is working: orange LCARS frame, warp starfield, and a working card with moving bar meters](docs/warp.jpg)

| Incoming hail: a thread needs input | Yellow alert: a thread needs approval | Red alert: a thread failed |
|---|---|---|
| ![Blue incoming hail with the LCARS question card](docs/hail.jpg) | ![Amber yellow alert while a command waits for approval](docs/yellow-alert.jpg) | ![Red alert after a failed run](docs/red-alert.jpg) |

## Copy/paste prompt

Paste one of these into a T3 Code thread. Claude does the rest.

**Theme only**

```text
Install the LCARS theme for T3 Code from https://github.com/peter-lewis/t3-lcars-theme.
Clone it to ~/dev/t3-lcars-theme (or pull it if it's already there), read its README, run ./install.sh,
then switch T3 Code to the "lcars" theme.
```

**Theme and sounds** (macOS)

```text
Install the LCARS theme and sounds for T3 Code from https://github.com/peter-lewis/t3-lcars-theme.
Clone it to ~/dev/t3-lcars-theme (or pull it if it's already there), read its README, run ./install.sh --sounds,
then switch T3 Code to the "lcars" theme.
```

**Uninstall**

```text
Uninstall the LCARS theme from https://github.com/peter-lewis/t3-lcars-theme: switch T3 Code back to the
"t3-code" theme, then run ./uninstall.sh from ~/dev/t3-lcars-theme.
```

## What you get

- **LCARS frame.** The sidebar ends in an LCARS elbow. Chats, replies, the composer, question cards and the thread details panel get LCARS panels, endcaps and segmented meters, set in the condensed Antonio typeface.
- **Status cards.** A working thread's sidebar card shows moving bar meters and a blinking endcap. A waiting thread shows thin standby cells.
- **Starfield.** Stars drift slowly behind the chat and jump to warp while the open thread is working.
- **Alert states.** These fade in on their own and clear when the condition does. The most severe one wins.

  | Condition | Alert | Color |
  |---|---|---|
  | A thread needs your input | Incoming hail | Blue |
  | A thread needs approval | Yellow alert | Amber |
  | A thread has failed | Red alert | Red |

  The stop button, the Submit button, the scrollbars and the glow follow the alert color.
- **Approval keys.** When a command waits for approval, Approve is a solid LCARS key in the alert color, Decline a red outline key and More a small outline key.
- **Light and dark.** In light appearance the console turns a pale, cool grey: LCARS bars on near-white panels with a deeper lavender, ink-speck stars that still go to warp, and darker alert hues so hail, yellow and red alert stay readable. T3 Code switches between them with its color scheme setting.
- **Reduced motion.** Animations stop when macOS *Reduce motion* is on.

![At rest: the starfield drifts slowly behind a finished thread](docs/idle.jpg)

| Light: at rest | Light: warp | Light: red alert |
|---|---|---|
| ![LCARS light mode at rest: grey background, orange and lavender LCARS frame](docs/light-idle.jpg) | ![LCARS light mode while working: ink starfield at warp, bar meters and the terminal drawer](docs/light-warp.jpg) | ![LCARS light mode in red alert](docs/light-red-alert.jpg) |

There is also `lcars-red-alert`, a manual variant that keeps the whole app in red alert until you switch back.

## Install by hand

```sh
git clone https://github.com/peter-lewis/t3-lcars-theme ~/dev/t3-lcars-theme
cd ~/dev/t3-lcars-theme
./install.sh            # theme only
./install.sh --sounds   # theme and sounds (macOS)
```

Then choose **LCARS** in T3 Code's theme settings.

`install.sh` copies the themes into `~/.t3/userdata/themes/`. They are copies, not symlinks, because T3 Code ignores symlinked themes. Re-run it after `git pull` to update. Anything it replaces is backed up next to the original as `*.bak-<timestamp>`.

**To turn the theme off,** pick any other theme. **To remove everything,** switch themes first, then run `./uninstall.sh`.

## Sounds (optional, macOS)

The sounds are [Claude Code hooks](https://docs.claude.com/en/docs/claude-code/hooks), so they work in T3 Code and in the `claude` CLI. The scripts synthesize all the audio; no samples are used.

| When | Sound |
|---|---|
| You send a prompt | Computer acknowledgement beep, then a quiet engine hum that fades in |
| Claude asks a question or needs permission | Hail chirp |
| Claude finishes | The hum fades out, then a completion beep |

Several sessions working at once share one hum. The hum stops on its own after 30 minutes.

`./install.sh --sounds` does the following:

1. Copies the scripts in `sounds/` to `~/.claude/hooks/lcars-sounds/` and generates the WAV files there.
2. Adds the `/sounds` command at `~/.claude/commands/sounds.md`.
3. Adds four hook entries to `~/.claude/settings.json` through `sounds/hooks.py`. Your other settings and hooks are left alone, and a backup is written first.

Restart Claude Code, or start a new T3 thread, to load the hooks.

**Turn them on and off** with `/sounds off`, `/sounds on`, `/sounds status`, or plain `/sounds` to flip. Without the command, run `python3 ~/.claude/hooks/lcars-sounds/toggle.py off`.

To change the sounds, edit `make_beeps.py` or `make_hum.py` and run `./install.sh --sounds` again.

## For agents installing this

If you are an AI agent following one of the prompts above:

1. Clone or pull the repo, then run `./install.sh`, adding `--sounds` only if the user asked for sounds.
2. Switch the theme. In T3 Code, call `t3_theme_set` with `themeId: "lcars"` if you have it. Otherwise tell the user to choose **LCARS** in T3 Code's theme settings.
3. If you installed sounds, tell the user that `/sounds off` turns them off and that the hooks load in new sessions.
4. To uninstall, switch the theme back to `t3-code` first, then run `./uninstall.sh`.

Do not symlink the theme files into `~/.t3/userdata/themes/`; T3 Code will not list them.

## Customizing

The whole theme is CSS inside `themes/lcars.json`. Edit the installed copy in `~/.t3/userdata/themes/`, then re-select the theme in T3 Code to reload it. Copy the file back into `themes/` when you're happy with it.

Helper scripts in `tools/`:

- `alerts.py <theme.json> [hail_icon yellow_icon red_icon]` regenerates the alert block at the end of the CSS, which is everything from `/* Ship alert states`. Passing other icon names lets you preview a look. For example, `python3 tools/alerts.py themes/lcars.json test-none message-circle-question-mark test-none` makes a question trigger yellow alert. Run it without icon names to restore the real triggers.
- `light.py themes/lcars.json` regenerates the light palette (`variants.light`) and the light-mode block, which sits just before `/* Ship alert states`. Every light colour comes from the `TOKENS` dict at the top, so retune it there, then re-run the script.
- `redalert.py themes/lcars.json themes/lcars-red-alert.json` rebuilds the red variant by color mapping. The red variant is dark only.
- `embed.py <theme.json> fonts/antonio.woff2` embeds the font.

### How it works

Everything is CSS keyed to T3 Code's markup:

- **Alerts** use `:root:has()` on the sidebar status icons. Input is `.lucide-message-circle-question-mark`, approval is `.lucide-shield-question-mark` and failed is `.lucide-circle-alert`.
- **Warp** runs while `button[aria-label="Stop generation"]` exists.
- **Stars and glow** sit on `[data-slot="sidebar-wrapper"]`, with the chat's wrappers made transparent so the LCARS elbow is the true edge.
- **Light mode** rules are scoped to `html:not(.dark)`, because T3 Code drops the `dark` class in light appearance. Star colors are the `--lc-s1`..`--lc-s3` variables, so light mode recolors the starfield without repeating it. Theme CSS is capped at 100,000 characters.
- **Fades** use registered `@property` color variables, so palette changes transition smoothly.

The selectors were found in T3 Code's bundle. To look yourself, run `npx @electron/asar extract "/Applications/T3 Code.app/Contents/Resources/app.asar" out`.

## Compatibility

Built against T3 Code Nightly in November 2026. The theme depends on T3 Code's internal markup, so an update can break parts of it. Issues and pull requests are welcome.

## Credits and license

- Theme, scripts and sounds: [MIT](LICENSE).
- [Antonio](https://github.com/googlefonts/antonioFont) font: SIL Open Font License 1.1 ([`fonts/OFL.txt`](fonts/OFL.txt)), embedded in the theme.

This is an unofficial fan project. It is not affiliated with or endorsed by Paramount or CBS Studios. Star Trek and LCARS are their trademarks.
