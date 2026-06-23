# Data sources & provenance

This project uses only **free, public** data. Nothing is scraped from behind a paywall.

| Layer | Source | What we take | License / notes |
|---|---|---|---|
| Match fixtures & results (all CL matches, groups → final) | [openfootball/champions-league](https://github.com/openfootball/champions-league) | date, stage, teams, score | Public domain (openfootball) |
| Ronaldo's goals + goal minutes per match | [Wikipedia](https://en.wikipedia.org) season pages (`2015–16 / 2016–17 / 2017–18 Real Madrid CF season`), raw wikitext `{{football box collapsible}}` + `{{goal}}` templates | goals scored, minute of each goal | CC BY-SA |
| Event-level data for the 3 finals (shots, xG, touches, coordinates) | [statsbomb/open-data](https://github.com/statsbomb/open-data) via `statsbombpy` | shots, xG, locations, touches | Free for public use under [StatsBomb's user agreement](https://github.com/statsbomb/open-data/blob/master/LICENSE.pdf) — please credit StatsBomb |

## Accuracy gate
`build_dataset.py` asserts the parsed per-season Champions League goal totals equal
Ronaldo's **official** tallies before writing any output:

| Season | Official CL goals | Parsed | Top scorer? |
|---|---|---|---|
| 2015–16 | 16 | 16 ✅ | Yes |
| 2016–17 | 12 | 12 ✅ | Yes |
| 2017–18 | 15 | 15 ✅ | Yes |

If Wikipedia formatting ever changes and breaks parsing, the build **fails loudly**
rather than producing wrong charts.

## Known simplifications
- Penalty-shootout goals are **not** counted as goals (standard in football stats), so
  Ronaldo's winning penalty in the 2016 final shootout is excluded from his goal totals.
- Assists are not included (Wikipedia goal templates don't encode them consistently).
- Event-level shot/touch detail is only available for the three finals.

## Credit
Please credit **StatsBomb** if you reuse the finals visuals, and **openfootball** /
**Wikipedia** contributors for the match and goal data.
