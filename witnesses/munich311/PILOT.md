# Pilot collation: Munich, BSB Cod. hebr. 311 against JTS 2367, narrative 13

Date: 28 September 2026. Section: the thirteenth narrative (Zion, prayer, *sha'atnez*), JTS 93b:18–94b:40.

## The witness

- Munich 311 (NLI Ktiv `990000612380205171`), 16th century, the commentary on fols. 1a–33b. The IIIF manifest is
  `manifest.json`; images are fetched with `py -3.13 witnesses/fetch_witness.py munich311 "Fol. 026r" "Fol. 033v"`.
- Images are about 1230 × 1700 px (JTS images are about 4000 × 5400). One Munich page holds about 28 lines.
- Narrative 13 runs from **26r:16** (`סיפור י"ב · הסיפור הי"ג והוא`) to **28v:19–21** (`ונשלם הסיפור ...`), about
  2.7 Munich pages against 2.5 JTS pages. Narrative 14 opens at 29r:1. The narrative numbering matches JTS.
- The hand is a clear Sephardi/Italian semi-cursive, more regular than JTS, and the text is continuous. The photographs
  are grey-scale microfilm scans; the lemmata are not visibly marked (no red), so lemma boundaries must come from JTS.

## Machine reading

- kraken, SoferMahir layout + `Italian_01` recognition (`py -3.13 witnesses/htr_witness.py munich311`), about 40 s/page.
- Layout: 24–28 main lines per page, cleanly segmented; a few short fragments at line ends and margins.
- Recognition is weak. A global letter alignment of the JTS text with the Munich machine reading matches **49%** of the
  JTS letters (`witnesses/collate_uncertain.py`); line-by-line trigram matching is too noisy to place lines reliably
  (median overlap 0.15, `witnesses/align_witness.py`). Typical errors: `א`/`מ`/`ח` confused, `ל`/`ו` dropped,
  `ﭏ` ligature for `של`.
- Conclusion: the machine reading is good enough to **find** the Munich line for a JTS passage, not to supply readings.
  Readings must be taken from the Munich image by eye. Munich line crops at 3× (`al_NNN/Main_NN_F.png`) are easy to read.

## What the Munich readings settle (checked in the images)

| JTS | JTS draft | Munich 311 | Effect |
|---|---|---|---|
| 93b:19 | `וכוין פתיחן ליה` | `וכוין פתיחן ליה בעליתיה נגד ירושלים` (26r:19) | Munich quotes Dan. 6:11 more fully |
| 93b:20 | `וירושלים רמז לגבורה[?]` | `וירושלים רמז למלכות` (26r:20) | Munich has the expected *Malkhut*; JTS image seems to read `לגבורה` — a real variant or a JTS slip |
| 93b:29 | `מקור והסתפקות לכל נושם[?]` | `מקור המסתפק לכל ונשם[?] שדי` (26v:5) | wording differs; not settled |
| 93b:30 | `הוא המסתפק לעקנא[?] מלך עולם` | `והוא מסתפק נקרא מלך עולם` (26v:6) | **`לעקנא` = `נקרא`** — resolves the uncertain word |
| 93b:30 | `שבזכות תפילת שחרית ...` | `ברכות התפילות ... שדי מלך עולם` (26v:4) | related wording |
| 93b:42–43 | `וכל זה בזכות שחרית מנחה ערבית` | `וכל זה בזכות שחרית מנחה וערבית` (26v:21) | confirms |
| 93b:47–48 | `הר הכתר עיר גדולה ... ומנגב דר הכית[?]` | `שהוא הר הבית עיר גדולה והיא ציון ... ומנגב הר הבית שהיא` (26v:27–28) | **`הר הבית`** — resolves 93b:48 and suggests JTS 47 `הכתר` should be rechecked |

Seven readings in about half an hour of image reading; two uncertain JTS words resolved, one probable JTS variant
(`לגבורה`/`למלכות`) documented, and one JTS reading (`הר הכתר`) flagged for recheck.

## Assessment and recommendation

- **Worth doing, but as a targeted collation, not a transcription.** Use the machine reading only to locate the passage;
  read the Munich image at the JTS `[?]` points and at the lemmata.
- Munich is a better-legible, independent copy: where JTS is faint or damaged (e.g. 93b:48, a blot), Munich often has
  a clean reading. It will be most useful for the folios with many open `[?]` (91a–92a, 90a–90b).
- A better recognition model would change the economics. Options: fine-tune `Italian_01` on ~200 hand-corrected Munich
  lines (kraken `ketos train`), or try `BiblIA_01`. Until then, budget about 1–2 minutes per `[?]` point.
- Next steps if continued: (1) extend the targeted reading to all `[?]` points of narrative 13; (2) record Munich readings
  in the JTS transcription notes as `Munich 311 fol:line reads …` (never replacing JTS silently); (3) add a Munich line to
  the translation pages' apparatus where it changes the sense.

## Extension: JTS 90a–92a (28 September 2026)

- Munich ↔ JTS: 89b:45 = 19v:1; 90a = 19v:3–20r:3; 90b = 20r:4–20v:34; 91a = 20v:34–21v:12; 91b = 21v:13–22v:14;
  92a = 22v:14–23v:6. Munich has no red, but the scribe writes lemma words in a larger hand.
- Method: the kraken line split failed on several of these pages (fragments), so the pages were read from
  overlapping 2× bands (`witnesses/bands.py`) and close-ups (`witnesses/zoom.py`). About 20–30 min per JTS folio.
- Results are in the dated "Munich 311 collation" notes of `transcription/089b.md` and `090a.md`–`092a.md`. Roughly
  50 JTS `[?]` words are resolved, about 40 confirmed, and a set of JTS readings is flagged for recheck. Main points:
  - 89b:45 `שמ"ו`[?] = `נעמי`; 90a:16 `תחו"ר`[?] = `חמו"ר`; 90a:23 `ובינים שמאת`[?] = `וביום שמחת` (Song 3:11).
  - 90b:4 lemma is `יש אם למקרא ויש אם למסורת` (B. Sanhedrin 4a); 90b:41 `עמדו ירות`[?] = `נעמי ורות`;
    90b:47 lemma = `וגן נעול אחותי`.
  - 91a:15 `והדר נכחים`[?] = `והררי נמרים`; 91a:22 = `ותשכב מרגלותיו`; 91a:24 `שכנתיך`[?] = `שפתותיך`; 91a:47 `כנגד`[?] = `גבריאל`.
  - 91b:7 `מעובר`[?] = `מעובד` (Obed); 91b:39 `הנוטה`[?] = `הנחש`; 91b:43 `הבית הנר`[?] = `הכתר הנקרא`; 91b:50 `הכהן`[?] = `ה'`.
  - 92a:5 `עם כן העפרים`[?] = `ועם בין העומדים` (Zech. 3:7); 92a:17 `לגיה`[?] = `בגי' אך`; **92a:18–20 Munich has `משה`
    where the JTS draft has `מנורה` three times** (as Oxford in the lemma `חונן הדעת משה`); 92a:37 `לצורה`[?] = `לבית`.
- Munich has two eye-skips in this stretch (90b:21–23, 92a:10–12), so it is an independent copy, not a source for JTS.
