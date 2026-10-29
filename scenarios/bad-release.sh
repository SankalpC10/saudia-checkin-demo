#!/usr/bin/env bash
# Ship the "loyalty miles per segment" bad release through the normal path:
# branch -> PR -> CI tests pass -> merge -> CI builds image and bumps deploy/ -> ArgoCD syncs.
# About 30% of check-ins (new loyalty members) then fail with ZeroDivisionError.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
BRANCH="feature/loyalty-miles-per-segment-$(date +%H%M%S)"
git checkout -q main && git pull -q
git checkout -qb "$BRANCH"
python3 - <<'PY'
p = "app/checkin.py"; s = open(p).read()
s = s.replace('''    per_pax_kg = booking["bags_kg"] / booking["passengers"]
''', '''    per_pax_kg = booking["bags_kg"] / booking["passengers"]
    loyalty = booking["loyalty"]
    # Show average loyalty miles earned per flown segment on the boarding pass
    miles_per_segment = loyalty["miles"] / loyalty["segments_flown"]
''')
s = s.replace('''        "status": "CHECKED_IN",''', '''        "loyalty_miles_per_segment": round(miles_per_segment),
        "status": "CHECKED_IN",''')
open(p, "w").write(s)
p = "tests/test_checkin.py"; s = open(p).read()
s += '''

def test_boarding_pass_shows_miles_per_segment():
    body = client.post("/checkin/ABC123").json()
    assert body["loyalty_miles_per_segment"] > 0
'''
open(p, "w").write(s)
PY
git commit -qam "feat: show loyalty miles per segment on the boarding pass"
git push -qu origin "$BRANCH"
PR=$(gh pr create --title "feat: show loyalty miles per segment on the boarding pass" \
  --body "Adds average loyalty miles per flown segment to the boarding pass response. Covered by a new test." \
  --base main --head "$BRANCH")
echo "PR: $PR"
gh pr checks "$PR" --watch >/dev/null
gh pr merge "$PR" --merge --delete-branch
git checkout -q main && git pull -q
echo "Merged. CI will build the image and bump deploy/; ArgoCD syncs within ~3 minutes."
