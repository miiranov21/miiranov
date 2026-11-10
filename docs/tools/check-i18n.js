// Проверка перевода интерфейса: node docs/tools/check-i18n.js <код языка>
// Файл docs/i18n/<код>.json должен содержать перевод каждой фразы из docs/i18n/_source.json.
const fs = require("fs"), path = require("path");
const dir = path.join(__dirname, "..", "i18n");
const src = JSON.parse(fs.readFileSync(path.join(dir, "_source.json"), "utf8"));
const lang = process.argv[2];
if (!lang){ console.log("usage: node check-i18n.js <lang>"); process.exit(2); }
let tr;
try { tr = JSON.parse(fs.readFileSync(path.join(dir, lang + ".json"), "utf8")); }
catch (e) { console.log("ERROR: file does not load as JSON: " + e.message); process.exit(1); }
let err = 0, warn = 0;
const E = m => { err++; if (err <= 40) console.log("ERROR " + m); };
const W = m => { warn++; if (warn <= 20) console.log("WARN  " + m); };
const ph = s => (s.match(/\{\d+\}/g) || []).sort().join(",");
for (const s of src){
  if (!(s in tr)) { E("missing: " + JSON.stringify(s)); continue; }
  const t = tr[s];
  if (typeof t !== "string" || (!t.trim() && s.trim())) { E("empty translation: " + JSON.stringify(s)); continue; }
  if (ph(s) !== ph(t)) E("placeholders differ: " + JSON.stringify(s) + " → " + JSON.stringify(t));
  if (lang !== "uk" && /[А-Яа-яЁё]{4,}/.test(t) && t === s && s.length > 3) W("left in Russian: " + JSON.stringify(s));
}
for (const k of Object.keys(tr)) if (!src.includes(k)) W("extra key not in source: " + JSON.stringify(k));
console.log((err ? "FAILED" : "OK") + ": " + src.length + " phrases, " + err + " errors, " + warn + " warnings");
process.exit(err ? 1 : 0);
