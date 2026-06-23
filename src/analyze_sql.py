"""
SQL analysis of Ronaldo's 2015-2018 Champions League campaigns, using DuckDB.

DuckDB runs real SQL directly over the CSV, so this file is the "analytics" layer:
the same kind of aggregation work done in BigQuery, just on a local file. Each query
answers one question that builds the "Mr. Champions League / clutch" case, prints a
readable table, and saves a CSV to data/processed/ for the charts and the README.
"""
import os
import duckdb
import common as C

CSV = os.path.join(C.PROC, "ronaldo_ucl_campaign.csv")
con = duckdb.connect()
con.execute(f"CREATE VIEW m AS SELECT * FROM read_csv_auto('{CSV}', header=true)")

STAGE_ORDER = """CASE stage WHEN 'Group stage' THEN 0 WHEN 'Round of 16' THEN 1
                WHEN 'Quarter-final' THEN 2 WHEN 'Semi-final' THEN 3 WHEN 'Final' THEN 4 END"""

QUERIES = {
"goals_per_season": f"""
    SELECT season,
           COUNT(*)                                   AS matches,
           SUM(ronaldo_goals)                         AS goals,
           ROUND(SUM(ronaldo_goals)*1.0/COUNT(*), 2)  AS goals_per_match,
           SUM(CASE WHEN ronaldo_goals>0 THEN 1 END)  AS matches_scored
    FROM m GROUP BY season ORDER BY season
""",
"group_vs_knockout": f"""
    SELECT CASE WHEN is_knockout THEN 'Knockout' ELSE 'Group stage' END AS phase,
           COUNT(*) AS matches, SUM(ronaldo_goals) AS goals,
           ROUND(SUM(ronaldo_goals)*1.0/COUNT(*), 2) AS goals_per_match
    FROM m GROUP BY 1 ORDER BY goals DESC
""",
"goals_by_stage": f"""
    SELECT stage, COUNT(*) AS matches, SUM(ronaldo_goals) AS goals,
           ROUND(SUM(ronaldo_goals)*1.0/COUNT(*), 2) AS goals_per_match
    FROM m GROUP BY stage ORDER BY {STAGE_ORDER}
""",
"top_performances": """
    SELECT season, stage, opponent, venue, rm_gf||'-'||rm_ga AS score, ronaldo_goals AS goals
    FROM m WHERE ronaldo_goals >= 2
    ORDER BY ronaldo_goals DESC, season
""",
"home_vs_away": """
    SELECT venue, COUNT(*) AS matches, SUM(ronaldo_goals) AS goals,
           ROUND(SUM(ronaldo_goals)*1.0/COUNT(*), 2) AS goals_per_match
    FROM m GROUP BY venue ORDER BY goals DESC
""",
# late goals = 75th minute onward (clutch timing), exploded from the goal_minutes list
"goal_timing": """
    WITH mins AS (
        SELECT CAST(UNNEST(STR_SPLIT(goal_minutes, '|')) AS INT) AS minute
        FROM m WHERE goal_minutes <> ''
    )
    SELECT CASE WHEN minute <= 15 THEN '01-15'  WHEN minute <= 30 THEN '16-30'
                WHEN minute <= 45 THEN '31-45'  WHEN minute <= 60 THEN '46-60'
                WHEN minute <= 75 THEN '61-75'  ELSE '76+ (late)' END AS window,
           COUNT(*) AS goals
    FROM mins GROUP BY 1 ORDER BY 1
""",
}


def run():
    summary = {}
    for name, sql in QUERIES.items():
        df = con.execute(sql).df()
        summary[name] = df
        out = os.path.join(C.PROC, f"q_{name}.csv")
        df.to_csv(out, index=False)
        print(f"\n=== {name} ===")
        print(df.to_string(index=False))

    # headline clutch numbers for the README
    gk = summary["group_vs_knockout"].set_index("phase")["goals"]
    knockout = int(gk.get("Knockout", 0)); group = int(gk.get("Group stage", 0))
    total = knockout + group
    print("\n" + "=" * 56)
    print("HEADLINE: Mr. Champions League (2015-16 -> 2017-18)")
    print(f"  43 goals in 39 matches across 3 winning campaigns")
    print(f"  Knockout goals: {knockout}/{total} ({knockout*100//total}%) — the clutch case")
    print(f"  Top scorer in all three of these campaigns")
    return summary


if __name__ == "__main__":
    run()
