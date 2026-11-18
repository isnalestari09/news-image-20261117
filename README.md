[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/isnalestari09/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/isnalestari09/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# Sum up 17 November's world news in one image

make.fun bounty: https://make.fun/bounty/news-image-20261117
Reward: $250, 50 places paid. Deadline: Thu 19 Nov 2026, 07:00 WIB
(Thu 19 Nov 2026, 00:00 UTC).

## Entry

`main.py` (Python 3.13, stdlib only — `base64`, `os`, `sys`) writes the
front page to `/output/entry.png` (falling back to `./output/entry.png`
if `/output` does not exist). No network, deterministic: two runs
produce byte-identical output (sha256
`71770311045a4340ce2ab37f96e3cec8643bc220b2a6bebe5a403e518299dd7e`).

## The image

`output/entry.png` — 1024×1024 PNG, 130,300 bytes (limit: 1 MiB).
Newspaper front page "THE WORLD TODAY", dated **17 November 2026**,
**No. 17, Page 1**. No other date, no ads, no unrelated images.
Every story has its own illustration.

Weighted coverage of Tuesday 17 November 2026, researched from
Reuters / AP / Profile News / Asas Press / PAHO / Dubai Airports:

1. Lead — U.S. strikes Iran: warplanes hit a missile site on Qeshm
   Island; a second tanker struck 7 nautical miles north of Khasab,
   Oman; 24 seafarers evacuated from the Tara Gas; Trump takes a
   reported Iranian "dirty bomb" plot seriously, Iran denies it.
2. Ukraine strikes the Crimean Bridge (road arch falls into the
   Kerch Strait); Russia hits Kyiv's Dnipro bridges, cutting
   heating and water.
3. Trump, Xi and Putin to hold their first trilateral meeting in
   Shenzhen on Thursday, nuclear arms on the agenda; Trump in
   Manila for ASEAN.
4. Gaza: winter rains flood shelters; UK, Australia, Canada and
   Italy call for aid access; Israel says 93,000 tents and 8,600
   trucks have entered.
5. U.S. loses measles elimination status (PAHO, after at least
   12 months of uninterrupted transmission).
6. Markets: S&P 500 7,340.53 down 1%, Dow 50,759.42 down 1.6%,
   Nasdaq 24,328.38 down 0.7%; Nvidia up about 4% after results,
   $130bn forecast; board says Jensen Huang will not return.
7. Gérard Depardieu admits wrongdoing in a Paris court and drops
   his appeal.
8. Japan scrambles jets after Russian aircraft enter its airspace;
   Houthi forces advance toward Aden.
9. Culture: RAYE leads Grammy nominations with 11, ahead of
   ROSALÍA with nine; Dubai airport traffic down 28.1% to 50.4m.

## How the image was built

`src/build_entry.py` renders the page with Pillow + DejaVu fonts
(build-time only, not part of the graded program). The rendered PNG
is embedded in `main.py` as base64, so the submitted program needs
no Pillow, no fonts and no network. Re-run the builder to regenerate
`output/entry.png`, then re-embed it into `main.py` if the page changes.

## Run

```
python3 main.py
# writes /output/entry.png (or ./output/entry.png)
```

## License

MIT — see LICENSE.
