// Проверка файла месяца программы: node docs/tools/validate-month.js <номер месяца> [<номер> ...]
// Ошибки (ERROR) нужно исправить, предупреждения (WARN) — по возможности.
const path = require("path");
const DOCS = path.join(__dirname, "..");
global.window = {};
require(path.join(DOCS, "program-en.js"));
const P = window.MD_PROGRAM.en;
const fs = require("fs");
const nums = process.argv.slice(2).map(Number).filter(Boolean);
if (!nums.length){ console.log("usage: node validate-month.js <month> [...]"); process.exit(2); }
// load all month files so cross-month duplicates are visible
for (let n = 1; n <= P.months.length; n++){ const f = path.join(DOCS, "program-en-m" + n + ".js"); if (fs.existsSync(f)) try { require(f); } catch (e) { if (nums.includes(n)) { console.log("ERROR m" + n + ": file does not load: " + e.message); process.exit(1); } } }
const LEN = { A1: [40, 140], A2: [100, 230], B1: [180, 330], B2: [250, 460], C1: [350, 620], C2: [400, 720] };
const MINW = { A1: [15, 70], A2: [40, 90], B1: [80, 140], B2: [140, 200], C1: [180, 280], C2: [220, 330] };
const cyr = /[а-яё]/i, lat = /[a-z]/i;
const wc = t => String(t).trim().split(/\s+/).filter(Boolean).length;
let errors = 0, warns = 0;
const E = (m, msg) => { errors++; console.log("ERROR m" + m + ": " + msg); };
const W = (m, msg) => { warns++; console.log("WARN  m" + m + ": " + msg); };
function checkQ(m, where, q, n){
  if (!q || typeof q.q !== "string" || !Array.isArray(q.a)) return E(m, where + ": bad question object");
  if (q.a.length !== (n || 3)) E(m, where + ": needs exactly " + (n || 3) + " options: " + q.q);
  if (q.c !== 0) E(m, where + ": c must be 0 (correct option first): " + q.q);
  if (new Set(q.a.map(x => String(x).toLowerCase().trim())).size !== q.a.length) E(m, where + ": duplicate options: " + q.q);
}
function checkWrite(m, where, w, level, nTrans){
  if (!w) return E(m, where + ": write missing");
  if (!Array.isArray(w.trans) || w.trans.length !== nTrans) E(m, where + ": write.trans must have " + nTrans + " items");
  (w.trans || []).forEach(([ru, acc], i) => {
    if (!ru || !cyr.test(ru)) E(m, where + ": trans[" + i + "] prompt must be Russian");
    if (!Array.isArray(acc) || !acc.length || acc.some(a => !lat.test(a) || cyr.test(a))) E(m, where + ": trans[" + i + "] needs English accepted answers");
    if (m >= 7){
      if (!ru.includes("___")) E(m, where + ": from month 7 trans prompts must contain ___ (gap fill): " + ru);
      if ((acc || []).some(a => wc(a) > 4)) E(m, where + ": from month 7 gap answers must be 1–4 words: " + ru);
    }
  });
  if (!w.prompt || !cyr.test(w.prompt)) E(m, where + ": write.prompt must be a Russian instruction");
  const [lo, hi] = MINW[level];
  if (!(w.minWords >= lo && w.minWords <= hi)) E(m, where + ": minWords " + w.minWords + " outside " + lo + "–" + hi + " for " + level);
  if (!Array.isArray(w.use) || w.use.length !== 4) E(m, where + ": write.use must list 4 words/phrases");
  if (!w.model || cyr.test(w.model)) E(m, where + ": write.model must be English");
  else {
    if (wc(w.model) < w.minWords * 0.8) W(m, where + ": model is shorter than 80% of minWords (" + wc(w.model) + "/" + w.minWords + ")");
    const low = " " + w.model.toLowerCase().replace(/[^a-z' -]/g, " ") + " ";
    (w.use || []).forEach(u => { if (!low.includes(" " + u.toLowerCase() + " ") && !low.includes(" " + u.toLowerCase())) W(m, where + ": model does not use «" + u + "»"); });
  }
}
function checkRead(m, where, r, level, nq){
  if (!r || !r.title || !r.text) return E(m, where + ": read needs title and text");
  if (cyr.test(r.text)) E(m, where + ": read.text must be English only");
  const n = wc(r.text), [lo, hi] = LEN[level];
  if (n < lo || n > hi) E(m, where + ": read.text has " + n + " words, need " + lo + "–" + hi + " for " + level);
  if (!Array.isArray(r.gloss)) E(m, where + ": read.gloss must be an array");
  if (!Array.isArray(r.qs) || r.qs.length !== nq) E(m, where + ": read.qs must have " + nq + " questions");
  (r.qs || []).forEach((q, i) => checkQ(m, where + " read.qs[" + i + "]", q));
}
function checkListen(m, where, l, nq){
  if (!l || !Array.isArray(l.lines) || l.lines.length < 6) return E(m, where + ": listen.lines needs at least 6 lines");
  l.lines.forEach(([who, t], i) => { if (!who || !t || cyr.test(t)) E(m, where + ": listen.lines[" + i + "] must be [speaker, English text]"); });
  if (!Array.isArray(l.qs) || l.qs.length !== nq) E(m, where + ": listen.qs must have " + nq + " questions");
  (l.qs || []).forEach((q, i) => checkQ(m, where + " listen.qs[" + i + "]", q));
}
const allWords = new Map();
for (let n = 1; n <= P.months.length; n++){ const M = P.months[n - 1]; (M.weeks || []).forEach((w, wi) => (w.words || []).forEach(x => { const k = String(x[0]).toLowerCase(); if (!allWords.has(k)) allWords.set(k, []); allWords.get(k).push(n + "." + (wi + 1)); })); }
for (const m of nums){
  const M = P.months[m - 1];
  if (!M){ E(m, "no such month"); continue; }
  const level = M.level;
  if (!Array.isArray(M.weeks) || M.weeks.length !== 4){ E(m, "needs exactly 4 weeks"); continue; }
  const seen = new Set();
  M.weeks.forEach((w, wi) => {
    const where = "week " + (wi + 1);
    if (!w.t || !cyr.test(w.t)) E(m, where + ": t must be a Russian title");
    if (!Array.isArray(w.words) || w.words.length !== 30) E(m, where + ": needs exactly 30 words");
    (w.words || []).forEach((x, i) => {
      if (!Array.isArray(x) || x.length !== 3) return E(m, where + ": words[" + i + "] must be [english, russian, transcription]");
      if (!lat.test(x[0]) || cyr.test(x[0])) E(m, where + ": words[" + i + "] english wrong: " + x[0]);
      if (!cyr.test(x[1])) E(m, where + ": words[" + i + "] russian wrong: " + x[1]);
      if (!cyr.test(x[2]) || lat.test(x[2])) E(m, where + ": words[" + i + "] transcription must be Russian letters: " + x[2]);
      const k = x[0].toLowerCase();
      if (seen.has(k)) E(m, where + ": duplicate word inside month: " + x[0]);
      seen.add(k);
      const other = (allWords.get(k) || []).filter(loc => !loc.startsWith(m + "."));
      if (other.length) E(m, where + ": word «" + x[0] + "» already used in month.week " + other.join(", "));
    });
    if (!Array.isArray(w.phrases) || w.phrases.length !== 6) E(m, where + ": needs exactly 6 phrases");
    (w.phrases || []).forEach(([e, r], i) => { if (!e || cyr.test(e) || !cyr.test(r || "")) E(m, where + ": phrases[" + i + "] must be [english, russian]"); });
    const g = w.grammar || {};
    if (!g.title || !g.text || !cyr.test(g.text)) E(m, where + ": grammar needs title and a Russian explanation text");
    if (!Array.isArray(g.examples) || g.examples.length < 4) E(m, where + ": grammar needs at least 4 examples");
    (g.examples || []).forEach(([e, r], i) => { if (!e || cyr.test(e) || !cyr.test(r || "")) E(m, where + ": examples[" + i + "] must be [english, russian]"); if (String(e).includes("—")) W(m, where + ": example contains «—», it will be skipped in tile exercises"); });
    if (!Array.isArray(g.quiz) || g.quiz.length !== 8) E(m, where + ": grammar.quiz needs exactly 8 questions");
    (g.quiz || []).forEach((q, i) => { checkQ(m, where + " quiz[" + i + "]", q); if (!String(q.q).includes("___")) E(m, where + " quiz[" + i + "]: question must contain ___"); });
    checkRead(m, where, w.read, level, 4);
    checkListen(m, where, w.listen, 4);
    if (!Array.isArray(w.speak) || w.speak.length !== 4 || w.speak.some(t => cyr.test(t))) E(m, where + ": speak must be 4 English sentences");
    checkWrite(m, where, w.write, level, 4);
  });
  const X = M.exam;
  if (!X){ E(m, "exam missing"); continue; }
  checkRead(m, "exam", X.read, level, 5);
  checkListen(m, "exam", X.listen, 5);
  checkWrite(m, "exam", X.write, level, 5);
  if (!Array.isArray(X.speak) || X.speak.length !== 5) E(m, "exam.speak must be 5 English sentences");
  if (!Array.isArray(X.grammar) || X.grammar.length !== 6) E(m, "exam.grammar must have 6 questions");
  (X.grammar || []).forEach((q, i) => { checkQ(m, "exam.grammar[" + i + "]", q); if (!String(q.q).includes("___")) E(m, "exam.grammar[" + i + "]: must contain ___"); });
}
console.log(errors ? "FAILED: " + errors + " errors, " + warns + " warnings" : "OK: 0 errors, " + warns + " warnings");
process.exit(errors ? 1 : 0);
