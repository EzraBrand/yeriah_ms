# Per-folio correction task (for a fresh agent)

You are correcting a machine transcription of one page of a 1392 Italian Hebrew cursive manuscript:
R. Reuven Tzarfati's commentary on Ha-Yeri'ah ha-Gedolah (JTS 2367). Kabbalistic content: sefirot
(כתר/מחשבה, חכמה, בינה, חסד/גדולה, פחד/גבורה, קו האמצעי/תפארת/ישראל, נצח, הוד, יסוד, מלכות/שכינה/עטרה),
Genesis 2–3 rivers of Eden, Jacob/Esau/Samael, biblical lemmas from the Yeri'ah.

Repo: `C:\Users\ezrab\Ezra Brandt\Claude\yeriah_ms\`. Folio id is like `077b`.

This Claude-root clone is the active shared working copy. The former clone at
`C:\Users\ezrab\Downloads\yeriah_ms\` is retained only as a reference and must not receive new edits.

Inputs for folio NNN:
- `htr/NNN_italian_logical.txt` — kraken draft, one numbered line per row, ~85% correct. Its numbering usually
  matches the crops (kraken line N = Main_NN) but can be offset by 1–2 when kraken emitted interlinear words or
  blank rows first. Align on content in the first batch and state the offset in the file header. Number the
  transcription by the crop (Main_NN), not by kraken.
- `al_NNN/Main_NN_R.png` and `Main_NN_L.png` — right and left halves of each main line, deskewed, 2x.
  A short line may be a single `Main_NN_F.png`. Ignore `Margin_*` files (out of focus, not needed now).
- `al_NNN/lines.tsv` — line list; last column `red` = red rubric ink near the line. The red bar marks a lemma
  quoted from the Yeri'ah (a biblical phrase or the Yeri'ah's own words). The bar sits in the interline space directly ABOVE the
  lemma, usually over its first word and its last word only (sometimes wavy). Bold the whole phrase between them.
  Trust the crops over the flag.
- `transcription/076b.md` and `077a.md` — finished examples of the output format and this scribe's habits.

Procedure:
1. Read the kraken text file once.
2. Read the crops in batches of at most 8 images (4 lines: R+L each). Right half first (Hebrew starts at right).
   Never send more than 8 images in one call. Do not re-read a line you have already transcribed.
3. After each batch, append corrected lines to `transcription/NNN.md` (create it on the first batch; header
   as in 077a.md). Keep the kraken line numbers. Mark uncertain words `[?]`, illegible `<..>`, bold lemmas.
   Keep scribal abbreviations as written (פי' , ואמ' , הנז' , פח' , חס' , ז"ל , אע"פ).
4. At the end add a short `## Notes` with the biblical sources of the lemmas and the sefirotic identifications.
5. Commit: `git add transcription/NNN.md && git -c user.name="Ezra Brandt" -c user.email="ezra.b@optimaxeyewear.com" commit -m "NNN corrected"`.
6. Also read the last two lines of the previous folio's transcription (if it exists) so line 1 joins correctly.
7. Report in 5 lines: lines done, count of `[?]`, lemmas found, anything odd.

Scribe habits seen so far: א often looks like a small ג-ל pair; final ך and ן are long; the abbreviation
stroke ' follows פי, ואמ, נק, לומ, כדא; ﭏ ligature for אל; "הפח'" = הפחד (Gevurah), "החס'" = החסד, "מה'" = מלכות/מדה;
"קו האמצעי" = Tiferet; "כדא'" = כדאיתא. Red bars above words mark lemmas. Skew is already corrected in the crops.
Work in Simplified Technical English; answer in English.
