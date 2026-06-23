"""
Build the Cristiano Ronaldo 2015-2018 Champions League match-by-match dataset.

Two reliable, free sources are merged:
  1. openfootball  -> the authoritative CL fixture list (every Real Madrid match,
     group stage -> final, with stage / opponent / score). This is what makes the
     dataset "Champions League only" (no La Liga, Copa, Super Cup or Club World Cup).
  2. Wikipedia raw wikitext -> per-match goalscorers, to attach Ronaldo's goals
     (and the minute of each goal) to those fixtures.

A correctness gate asserts the per-season totals equal Ronaldo's official CL tallies
(16 / 12 / 15), so if Wikipedia formatting ever drifts, the build fails loudly.

Output: data/processed/ronaldo_ucl_campaign.csv
"""
import re, csv, os
import common as C

STAGE_MAP = {
    "Round of 16": "Round of 16", "Quarterfinals": "Quarter-final",
    "Semifinals": "Semi-final", "Final": "Final",
}
STAGE_ORDER = {"Group stage": 0, "Round of 16": 1, "Quarter-final": 2, "Semi-final": 3, "Final": 4}
DASH = {"–": "-", "—": "-", "−": "-"}


def norm_dash(s):
    for k, v in DASH.items():
        s = s.replace(k, v)
    return s


def parse_openfootball(season):
    """Return Real Madrid's CL matches for a season: stage, opponent, venue, score."""
    of = C.SEASONS[season]["of"]
    txt = C.http_get(
        f"https://raw.githubusercontent.com/openfootball/champions-league/master/{of}/cl.txt",
        cache_name=f"openfootball_{of}.txt")
    stage, matches = None, []
    # capture both teams + the trailing score string (which may include "pen." / "a.e.t.")
    line_re = re.compile(r"(.+?)\s+\(([A-Z]{3})\)\s+v\s+(.+?)\s+\(([A-Z]{3})\)\s+(\d.+)$")
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("▪"):  # ▪ stage header
            name = s[1:].strip()
            stage = "Group stage" if name.startswith("Group") else STAGE_MAP.get(name, name)
            continue
        m = line_re.search(line)
        if not m:
            continue
        home, _, away, _, score_str = m.groups()
        home = re.sub(r"^\d{1,2}:\d{2}\s*", "", home.strip())
        away = re.sub(r"^\d{1,2}:\d{2}\s*", "", away.strip())
        if "Real Madrid" not in (home, away):
            continue
        # "5-3 pen. 1-1 a.e.t." -> match score is the 1-1; record the shootout winner separately
        pen = re.search(r"(\d+)-(\d+)\s*pen\.\s*(\d+)-(\d+)", score_str)
        if pen:
            ph, pa, hs, as_ = map(int, pen.groups())
            home_won = ph > pa
        else:
            hs, as_ = map(int, re.search(r"(\d+)-(\d+)", score_str).groups())
            home_won = None
        is_home = (home == "Real Madrid")
        gf, ga = (hs, as_) if is_home else (as_, hs)
        if home_won is None:
            result = "W" if gf > ga else "L" if gf < ga else "D"
        else:
            result = "W" if home_won == is_home else "L"  # decided on penalties
        matches.append(dict(
            season=season, stage=stage,
            opponent=away if is_home else home,
            venue="Home" if is_home else "Away",
            rm_gf=gf, rm_ga=ga, of_result=result,
        ))
    return matches


def parse_wiki_goals(season):
    """Return every Real Madrid match box (all competitions) with Ronaldo's goal minutes.

    We do NOT try to detect the competition here; the openfootball CL fixture list is
    the authoritative filter at join time. We keep the `round` text only as a tiebreaker.
    """
    wt = C.wiki_raw(C.SEASONS[season]["wiki"], cache_name=f"wiki_{season}.txt")
    boxes = []
    for b in C.extract_templates(wt, "football box collapsible"):
        d = C.split_params(b)
        t1, t2 = d.get("team1", ""), d.get("team2", "")
        if "realmadrid" not in (C.norm_token(t1) + "|" + C.norm_token(t2)):
            continue
        rm_home = "realmadrid" in C.norm_token(t1)
        sm = re.search(r"(\d+)\D+(\d+)", norm_dash(d.get("score", "")))
        if not sm:
            continue
        hs, as_ = int(sm.group(1)), int(sm.group(2))
        goals_field = d.get("goals1", "") if rm_home else d.get("goals2", "")
        mins = []
        for gm in re.finditer(r"Ronaldo[^\n]*?\{\{goal\|([^}]*)\}\}", goals_field):
            for a in gm.group(1).split("|"):
                mm = re.match(r"\s*(\d+)", a)
                if mm:
                    mins.append(int(mm.group(1)))
        boxes.append(dict(
            opp_token=C.norm_token(t2 if rm_home else t1),
            venue="Home" if rm_home else "Away",
            rm_gf=hs if rm_home else as_, rm_ga=as_ if rm_home else hs,
            round=C.clean_name(d.get("round", "")),
            goals=len(mins), minutes=sorted(mins)))
    return boxes


def _round_matches_stage(round_text, stage):
    """Tiebreaker: does a Wikipedia `round` value plausibly belong to this CL stage?"""
    r = round_text.lower()
    if stage == "Group stage":
        return r in {"1", "2", "3", "4", "5", "6"}
    if stage == "Final":
        return "final" in r
    return "leg" in r  # Round of 16 / QF / SF are two-legged


def build():
    rows = []
    for season in C.SEASONS:
        fixtures = parse_openfootball(season)
        wiki = parse_wiki_goals(season)
        for fx in fixtures:
            opp_tok = C.norm_token(fx["opponent"])
            # candidates share venue + exact score with the CL fixture
            cand = [w for w in wiki if w["venue"] == fx["venue"]
                    and w["rm_gf"] == fx["rm_gf"] and w["rm_ga"] == fx["rm_ga"]]
            # narrow by opponent token (fuzzy 4-char overlap handles name spelling diffs)
            opp_cand = [w for w in cand if opp_tok and
                        (opp_tok[:4] in w["opp_token"] or w["opp_token"][:4] in opp_tok)] or cand
            # if still ambiguous, prefer the box whose round matches the CL stage
            best = None
            if len(opp_cand) > 1:
                staged = [w for w in opp_cand if _round_matches_stage(w["round"], fx["stage"])]
                best = (staged or opp_cand)[0]
            elif opp_cand:
                best = opp_cand[0]
            fx["ronaldo_goals"] = best["goals"] if best else 0
            fx["goal_minutes"] = "|".join(map(str, best["minutes"])) if best else ""
            fx["matched"] = best is not None
            fx["is_knockout"] = fx["stage"] != "Group stage"
            fx["result"] = fx.pop("of_result")  # respects penalty-shootout outcomes
            rows.append(fx)

    rows.sort(key=lambda r: (r["season"], STAGE_ORDER.get(r["stage"], 9)))

    # ---- correctness gate ----
    print("=== Ronaldo Champions League goals per campaign ===")
    ok = True
    for season, known in C.KNOWN_UCL_GOALS.items():
        got = sum(r["ronaldo_goals"] for r in rows if r["season"] == season)
        flag = "OK" if got == known else "!! MISMATCH"
        if got != known:
            ok = False
        print(f"  {season}: parsed {got:>2}  (official {known})  {flag}")
    total = sum(r["ronaldo_goals"] for r in rows)
    print(f"  TOTAL: {total} goals across the three winning campaigns")

    cols = ["season", "stage", "opponent", "venue", "rm_gf", "rm_ga", "result",
            "is_knockout", "ronaldo_goals", "goal_minutes", "matched"]
    out = os.path.join(C.PROC, "ronaldo_ucl_campaign.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in cols})
    print(f"\nWrote {len(rows)} matches -> {out}")
    if not ok:
        raise SystemExit("Correctness gate FAILED — goal totals do not match official records.")
    return rows


if __name__ == "__main__":
    build()
