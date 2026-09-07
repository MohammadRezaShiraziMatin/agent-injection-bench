# Private GitHub + tag `v0.1-pilot`

No secrets in git. Run on the machine that has the Phase A tree after a successful (or intentionally partial) pilot.

## Create / link private repo

If the folder is not yet a GitHub remote:

```bash
cd /path/to/agent-injection-bench
git status
# ensure .env is not staged
git check-ignore -v .env

# Option A: GitHub CLI
gh repo create agent-injection-bench --private --source=. --remote=origin --push

# Option B: existing empty private repo
git remote add origin https://github.com/<USER>/agent-injection-bench.git
git push -u origin main
```

## Tag the pilot

Tag the commit that closes Phase A packaging (and ideally after live runs + `results/phase_a_summary.json` produced locally — summary JSON is gitignored; the tag marks the code+docs freeze):

```bash
git fetch origin
git checkout main
git pull origin main
git tag -a v0.1-pilot -m "AIB v0.1 pilot: D0 undefended harness, 20+20 twins, ASR L0 stubs, Phase A packaging"
git push origin v0.1-pilot
# verify
git show v0.1-pilot --no-patch
```

## Honesty reminder

The tag means **pilot packaging**, not a published leaderboard. Do not attach fabricated ASR/utility to the release notes. Point readers to `PHASE_A.md` and `results/phase_a_summary.json` on the researcher machine when real traces exist.
