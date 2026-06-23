"""
Run the whole Ronaldo Champions League pipeline end to end:
  1. build_dataset  -> fetch (openfootball + Wikipedia), parse, validate, write CSV
  2. analyze_sql    -> DuckDB SQL aggregations -> data/processed/q_*.csv
  3. viz_campaign   -> campaign charts -> outputs/01..04
  4. viz_finals     -> StatsBomb shot maps + heatmaps -> outputs/05..06

Usage:  python run_all.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import build_dataset, analyze_sql, viz_campaign, viz_finals

if __name__ == "__main__":
    print("\n[1/4] Building dataset ...");   build_dataset.build()
    print("\n[2/4] Running SQL analysis ..."); analyze_sql.run()
    print("\n[3/4] Campaign charts ...");      viz_campaign.run()
    print("\n[4/4] Finals visuals ...");       viz_finals.run()
    print("\nDone. See outputs/ for charts and data/processed/ for tables.")
