# پرامپت عامل: P4.2 Primary Paired Live D0↔D2 (فقط این Scope)

تو عامل مهندسی روی مخزن **`agent-injection-bench`** هستی. **تنها** کار تو اجرای واقعی، reproducible و قرارداد‌محور آزمایش **P4.2 Primary Paired Live D0↔D2** است. هر کار دیگری ممنوع است.

---

## Scope (الزامی)

**مجاز:**

- بررسی وضعیت git/workspace
- خواندن قراردادها و manifestهای موجود
- زنجیره gate → dry-run → (در صورت مجوز صریح operator) live → scoring → post-validation
- استفاده از runner/scorer/verifier **موجود** با `--p42-primary-config`

**ممنوع:**

- refactor
- dataset work / regeneration
- P4.3 re-run یا live P4.3
- runner / scorer / contract جدید یا implementation موازی
- تغییر خارج از Scope (شامل رفع `upstream_weight_revision=UNVERIFIED`)
- overwrite نتایج قبلی یا artifactهای immutable
- فعال‌کردن live بدون PASS کامل gateها و (برای live) مجوز صریح operator در همان task

---

## ثابت‌های baseline (برای تطبیق؛ hard-code نکن مگر برای verify)

| مورد | مقدار |
|------|--------|
| Branch کار | `cursor/p4-2-dataset-6db2` |
| Commit مرجع (حداقل) | `b3a9e36` — «P4.2 primary paired runner, FPR scorer alignment, and D2 live gate wiring» |
| P4.2 dataset digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| P4.3 dataset digest (integrity فقط) | `e60969bee257ec3111febf215fb5f7079edb79ed050dae300e549336184ab53d` |
| AdaptiGuard commit (model-lock) | `30ddc756a07e3eae1f9afd5a3e9b9c68a7017f64` |
| خروجی paired P4.2 primary | `results/p4_2_paired/<RUN_ID>/` |
| Cohort | از `load_p42_primary_run_config()` و `artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json` — **نه** لیست دستی ID در پرامپت |

**محدودیت علمی (فقط گزارش):** `upstream_weight_revision = UNVERIFIED` — خارج از Scope؛ برای رفع آن تغییری نده.

---

## 1. ابتدا وضعیت واقعی را بررسی کن

قبل از هر تغییر یا اجرا:

```bash
git fetch --all --prune
git status --short
git branch --show-current
git log -5 --oneline
git rev-parse HEAD
```

سپس **HEAD**، **branch** و تغییرات واقعی workspace را با baseline تطبیق بده:

- Branch مورد انتظار: `cursor/p4-2-dataset-6db2`
- Expected commit context: `b3a9e36` یا commit‌های بعدی **همان branch**
- P4.2 digest باید با مقدار بالا یکسان بماند

**اگر branch/HEAD با baseline متفاوت است:**

1. divergence را گزارش کن (commitهای ahead/behind، فایلهای modified/untracked روی `data/` یا `schema/`).
2. فقط اگر قراردادهای فعلی (freeze، integrity، runner `--p42-primary-config`) همان Scope را **تأیید** می‌کنند ادامه بده؛ در غیر این صورت **STOP**.

**اگر روی `main` هستی:** به `cursor/p4-2-dataset-6db2` checkout کن (یا branch معادل با همان قراردادها) و دوباره verify کن.

---

## 2. Contracts و implementation موجود را بخوان

حداقل این مسیرها را بخوان (بدون تغییر مگر STOP به §3):

```text
data/episodes_p4_2/MANIFEST.json
artifacts/p4_2_primary_d0_d2_experiment/MANIFEST.json
artifacts/p4_2_primary_d0_d2_experiment/READINESS.json
artifacts/p4_2_d2_live_approval.json

config/p4_3_d2_eval_gate.v1.json
config/p4_3_live_eval_gate.v1.json
config/p4_3_paired_eval_contract.v1.json
config/p4_3_evaluation_metrics.v1.json

scripts/run_p4_3_paired_benchmark.py
scripts/p4_3_paired_common.py
scripts/verify_p4_2_d2_live_approval.py
```

**Integration (فقط validation، بدون edit):**

```text
agent/defense/
```

اگر validation یک **defect قراردادی واقعی** در کد را ثابت کند → **STOP**؛ workaround یا patch موازی نساز.

**Runner (reuse اجباری):**

```bash
python3 scripts/run_p4_3_paired_benchmark.py --p42-primary-config [--live] --run-id <UNIQUE_ID>
```

- Cohort، utility/FPR scope، digest و مسیر خروجی را **فقط** از `load_p42_primary_run_config()` و manifestهای P4.2 primary بگیر.
- episode IDها را در اسکript/agent hard-code نکن.

**Scoring (بعد از live):**

```bash
python3 scripts/score_p4_3_paired_metrics.py results/p4_2_paired/<RUN_ID>
```

---

## 3. Immutable Rules

**بدون مجوز صریح در task تغییر نده:**

```text
data/episodes_p4_2/**
schema/**
historical results (به‌ویژه results/p4_3_*)
artifacts/p4_2_d2_live_approval.json
artifacts/p4_3_d2_live_approval.json
model-lock artifacts
config/p4_3_live_eval_gate.v1.json
coverage/eligibility artifacts
existing contracts (مگر operator gate §6 با مجوز صریح human)
```

به‌خصوص:

- P4.2 digest **نباید** تغییر کند.
- historical `results/p4_3_*` **نباید** تغییر کند.
- dataset regeneration ممنوع.
- overwrite run قبلی ممنوع (`--run-id` یکتا).
- artifact موازی برای همان experiment نساز.

اگر integrity یا contract مشکل دارد → **STOP** و گزارش دقیق؛ workaround نساز.

---

## 4. Gate Chain (ترتیب اجباری)

```bash
python3 scripts/verify_p4_2_freeze.py
python3 scripts/verify_p4_3_integrity.py
python3 scripts/verify_model_lock.py
python3 scripts/verify_d2_integration.py
python3 scripts/live_eval_preflight.py
python3 scripts/verify_p4_2_d2_live_approval.py
```

هر verifier/preflight دیگری که `RUN_MANIFEST`، `READINESS.json`، یا runner فعلی **الزام** کرده را هم اجرا کن و در گزارش gate بیاور.

### STOP Conditions (هیچ live call)

در صورت **هرکدام** از موارد زیر → **متوقف**؛ live اجرا نکن:

| شرط |
|-----|
| `verify_p4_2_freeze.py` FAIL |
| `verify_p4_3_integrity.py` FAIL |
| model lock ≠ `LOCKED` |
| `verify_d2_integration.py` FAIL |
| `live_eval_preflight.py` FAIL |
| P4.2 approval: `ok != true` (قبل از live) |
| `scope_ok != true` |
| fallback فعال برای target/judge |
| provider routing مبهم یا ناسازگار با model-lock |
| `OPENROUTER_API_KEY` موجود نیست (برای live) |
| run ID collision (مسیر `results/p4_2_paired/<RUN_ID>` از قبل وجود دارد) |
| `git diff` روی `data/` یا `schema/` |
| هویت target/judge در contract/manifest نامشخص |

**تفکیک gate P4.2 از P4.3:**

- Live P4.2 primary از `p4_2_primary_preflight` در `config/p4_3_d2_eval_gate.v1.json` و `verify_p4_2_d2_live_approval.py` تبعیت می‌کند.
- **Global** `preflight.live_d2_inference_allowed` (P4.3) را برای P4.2 primary **تغییر نده**.

---

## 5. Dry-run اجباری (قبل از هر live)

```bash
python3 scripts/run_p4_3_paired_benchmark.py \
  --p42-primary-config \
  --run-id p42-primary-d0-d2-dry-pre-live-<UTC>
```

`<UTC>` = timestamp یکتا (مثلاً `20260921T173000Z`).

Dry-run باید طبق contract/manifest نشان دهد:

| انتظار | مقدار |
|--------|--------|
| `n_episodes` | 18 |
| `target_api_calls` | 0 |
| `judge_api_calls` | 0 |
| P4.2 digest | `4b2e6f592118cb9c419ed11dd9574125584ebbb325709ae5fc048543a1ba9dee` |
| output root | `results/p4_2_paired/` |

شواهد را از `RUN_MANIFEST.json` همان dry-run استخراج کن.

اگر dry-run با contract **تطابق ندارد** → **STOP**.

---

## 6. Operator Gate (فقط با مجوز صریح human در همان task)

**پیش‌فرض:** `config/p4_3_d2_eval_gate.v1.json` → `p4_2_primary_preflight.live_d2_inference_allowed = false` → live **BLOCKED**.

**فقط اگر** در task صریحاً نوشته شده operator مجاز است live P4.2 را فعال کند:

1. تنها این فیلد را set کن:  
   `p4_2_primary_preflight.live_d2_inference_allowed = true`
2. **Global** P4.3 `preflight.live_d2_inference_allowed` را **تغییر نده**.
3. دوباره:

```bash
python3 scripts/verify_p4_2_d2_live_approval.py
```

باید: `scope_ok = true` و `ok = true`.

اگر `ok` هنوز false است → live اجرا نکن؛ گزارش: `OPERATOR_GATE_ACTIVATION_REQUIRED`.

---

## 7. Live Execution

**فقط** بعد از PASS همه gateها + dry-run + (در صورت live) operator gate:

```bash
export RUN_ID="p42-primary-d0-d2-$(date -u +%Y%m%dT%H%M%SZ)-controlled"

python3 scripts/run_p4_3_paired_benchmark.py \
  --p42-primary-config \
  --live \
  --run-id "$RUN_ID"
```

الزامات اجرا:

- دقیقاً cohort تعریف‌شده توسط manifest / `load_p42_primary_run_config()`
- ترتیب: **D0 سپس D2** طبق runner contract
- هر episode: **target سپس judge** طبق contract
- target/judge **locked**؛ `fallback=false`
- routing مطابق model-lock
- secrets در log ممنوع
- `RUN_ID` یکتا؛ overwrite ممنوع
- raw evidence در ساختار موجود پروژه (`D0/`, `D2/`, `paired/`, traces)
- هیچ historical `results/p4_3_*` تغییر نکند

در صورت خطا یا partial run → live را ادامه نده (§10).

---

## 8. Scoring

```bash
python3 scripts/score_p4_3_paired_metrics.py results/p4_2_paired/$RUN_ID
```

فقط metrics تعریف‌شده در contract/scorer:

- ASR
- S2 / S3 / S4 rates
- Utility
- FPR
- paired transitions
- Paired Defense Rate **فقط** اگر denominator معتبر باشد

metric جدید تعریف نکن. نتایج **descriptive**؛ از superiority claim خودداری کن.

---

## 9. Post-run Validation

```bash
python3 scripts/verify_p4_2_freeze.py
python3 scripts/verify_p4_3_integrity.py
git diff -- data/ schema/ artifacts/p4_2_d2_live_approval.json
python3 -m pytest tests/test_d2_paired_eval.py tests/test_p4_3_fpr_scorer.py -q
```

validator اختصاصی run (اگر در repo وجود دارد) را هم اجرا کن.

**چک‌لیست run کامل (همه باید برقرار باشد برای final evidence):**

- [ ] `RUN_MANIFEST.json` موجود
- [ ] 18 episode (9 attack + 9 benign)
- [ ] 9 `pair_id` معتبر
- [ ] P4.2 digest صحیح در manifest
- [ ] target/judge identity ثبت شده
- [ ] routing ثبت شده
- [ ] seed ثبت شده
- [ ] `adaptiguard_commit` ثبت شده
- [ ] evidence D0 و D2 برای همان episode set
- [ ] live: target/judge API calls > 0
- [ ] historical P4.3 untouched
- [ ] `data/` / `schema/` untouched

run ناقص = final evidence **نیست**.

---

## 10. Failure Handling

- live را در صورت failure ادامه نده
- نتایج ناقص را final معرفی نکن
- run directory را preserve کن
- historical / data / schema را restore یا overwrite نکن
- workaround implementation نساز
- علت + evidence (log، exit code، مسیر run) گزارش کن
- gate را خودسرانه تغییر نده مگر §6 با مجوز صریح task

---

## 11. Acceptance Criteria

برای هر AC فقط: **`PASS` / `FAIL` / `BLOCKED`** + evidence کوتاه.

| AC | معیار |
|----|--------|
| AC1 | P4.2 digest unchanged |
| AC2 | تمام live gates PASS (یا BLOCKED قبل از live) |
| AC3 | دقیقاً 18 episode طبق manifest |
| AC4 | 9 pair_id معتبر |
| AC5 | D0 سپس D2 طبق contract |
| AC6 | locked target/judge + routing صحیح |
| AC7 | episode evidence + RUN_MANIFEST |
| AC8 | scorer مطابق contract |
| AC9 | seed/models/routing در manifest |
| AC10 | هیچ immutable artifact تغییر نکرده |
| AC11 | tests/validators PASS |
| AC12 | Scientific status = PASS / PASS WITH CONDITIONS / BLOCKED |

**Limitation ثابت (همیشه گزارش):** `upstream_weight_revision = UNVERIFIED`

---

## 12. Final Output — دقیقاً فقط این ۵ بخش

خروجی نهایی تو **فقط** این ساختار باشد (بدون بخش اضافه):

### وضعیت اجرا

- HEAD
- branch
- run_id (یا `N/A` اگر BLOCKED)
- `scope_ok` / `ok` (از `verify_p4_2_d2_live_approval.py`)
- gate status (جدول یا لیست PASS/FAIL)
- live executed / **BLOCKED**

### تغییرات

فقط فایل‌هایی که واقعاً تغییر کرده‌اند + دلیل.  
اگر source change نشده:

```text
No source change.
```

### validation/test results

جدول:

```text
command | result | evidence
```

### Acceptance Criteria

```text
AC1 PASS/FAIL/BLOCKED — evidence
...
AC12 PASS/FAIL/BLOCKED — evidence
```

### موارد باقی‌مانده

فقط blocker یا step **verified** (مثلاً `OPERATOR_GATE_ACTIVATION_REQUIRED`).  
اگر scope کامل شد:

```text
No verified blocker remains for this scope.
```

---

## اصل نهایی (ترتیب اجرا)

```text
freeze → integrity → model lock → D2 integration → preflight → P4.2 approval/gate → dry-run → [operator gate اگر مجاز] → live → scoring → validation
```

در failure هر مرحله: **متوقف**؛ فقط evidence واقعی همان blocker را گزارش کن.

---

## پیوست: دستورات مرجع سریع

```bash
# Gates
python3 scripts/verify_p4_2_freeze.py
python3 scripts/verify_p4_3_integrity.py
python3 scripts/verify_model_lock.py
python3 scripts/verify_d2_integration.py
python3 scripts/live_eval_preflight.py
python3 scripts/verify_p4_2_d2_live_approval.py

# Dry-run
python3 scripts/run_p4_3_paired_benchmark.py --p42-primary-config --run-id p42-primary-d0-d2-dry-pre-live-<UTC>

# Live (فقط پس از همه PASS + operator اگر لازم)
export RUN_ID="p42-primary-d0-d2-$(date -u +%Y%m%dT%H%M%SZ)-controlled"
python3 scripts/run_p4_3_paired_benchmark.py --p42-primary-config --live --run-id "$RUN_ID"

# Score
python3 scripts/score_p4_3_paired_metrics.py "results/p4_2_paired/$RUN_ID"
```
