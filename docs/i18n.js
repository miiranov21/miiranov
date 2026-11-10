// Интерфейс на разных языках. Приложение написано по-русски; этот модуль подменяет русские фразы на экране
// переводом из i18n/<язык>.json. {0}, {1}… в словаре — значения, которые приложение подставляет само (числа, имена, даты).
(function(){
  "use strict";
  const LANGS = {
    ru: { name: "Русский", locale: "ru-RU" }, en: { name: "English", locale: "en-GB" }, es: { name: "Español", locale: "es-ES" },
    de: { name: "Deutsch", locale: "de-DE" }, fr: { name: "Français", locale: "fr-FR" }, pt: { name: "Português", locale: "pt-BR" },
    pl: { name: "Polski", locale: "pl-PL" }, tr: { name: "Türkçe", locale: "tr-TR" }, az: { name: "Azərbaycanca", locale: "az-Latn-AZ" },
    uk: { name: "Українська", locale: "uk-UA" }, zh: { name: "中文", locale: "zh-CN" }
  };
  const KEY = "moy-den-lang";
  function detect(){
    const list = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || "ru"]);
    for (const l of list){ const c = String(l).toLowerCase().slice(0, 2); if (LANGS[c]) return c; }
    return "en";
  }
  let lang = null;
  try { lang = localStorage.getItem(KEY); } catch (e) {}
  if (!lang || !LANGS[lang]){ lang = detect(); try { localStorage.setItem(KEY, lang); } catch (e) {} }

  const CYR = /[А-Яа-яЁё]/;
  const SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, PRE: 1, NOSCRIPT: 1 };
  const ATTRS = ["placeholder", "aria-label", "title", "alt"];
  let exact = new Map(), lower = new Map(), buckets = new Map(), ready = false;
  const done = new WeakMap();   // text node -> the value we set (to skip our own changes)

  const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  function build(dict){
    for (const [src, dst] of Object.entries(dict)){
      if (!dst) continue;
      if (!/\{\d+\}/.test(src)){ exact.set(src, dst); const lo = src.toLowerCase(); if (!lower.has(lo)) lower.set(lo, dst); continue; }
      // template: literal parts must match exactly, {n} matches any text
      const parts = src.split(/(\{\d+\})/);
      const order = [];
      const re = new RegExp("^" + parts.map(p => { const m = p.match(/^\{(\d+)\}$/); if (m){ order.push(+m[1]); return "(.*?)"; } return esc(p).replace(/ /g, "\\s*"); }).join("") + "$");
      const lead = parts[0] && parts[0].length >= 3 ? parts[0].slice(0, 3).toLowerCase() : "*";
      if (!buckets.has(lead)) buckets.set(lead, []);
      buckets.get(lead).push({ re, order, dst, lits: parts.filter(p => !/^\{\d+\}$/.test(p)).join("").length });
    }
    // longer literal text first: more specific templates win
    for (const list of buckets.values()) list.sort((a, b) => b.lits - a.lits);
  }
  function cap(src, dst){ return src && dst && src[0] !== src[0].toLowerCase() ? dst[0].toUpperCase() + dst.slice(1) : dst; }
  function tr(core, depth){
    if (exact.has(core)) return exact.get(core);
    const lo = core.toLowerCase();
    if (lower.has(lo)) return cap(core, lower.get(lo));
    if (depth > 2) return null;
    const cands = (buckets.get(lo.slice(0, 3)) || []).concat(buckets.get("*") || []);
    for (const t of cands){
      const m = core.match(t.re); if (!m) continue;
      const vals = {}; t.order.forEach((n, i) => { const v = m[i + 1]; vals[n] = CYR.test(v) ? (tr(v.trim(), depth + 1) || piecewise(v) || v) : v; });
      return t.dst.replace(/\{(\d+)\}/g, (a, n) => vals[n] !== undefined ? vals[n] : a);
    }
    return null;
  }
  // last resort: translate the known words and phrases between numbers and punctuation
  function piecewise(core){
    const bits = core.split(/(\s*[0-9]+(?:[.,][0-9]+)?\s*|\s*[,:;·•\/()«»"!?.—–+=%]+\s*)/);
    let changed = false;
    const out = bits.map(b => { if (!b || !CYR.test(b)) return b; const t = tr(b.trim(), 3); if (t){ changed = true; return b.replace(b.trim(), t); } return b; });
    return changed ? out.join("") : null;
  }
  function translateText(s){
    if (!s || !CYR.test(s)) return null;
    const m = s.match(/^(\s*)([\s\S]*?)(\s*)$/);
    const core = m[2].replace(/\s+/g, " ");
    let t = tr(core, 0);
    if (t === null){
      // emoji, bullets and quotes around a phrase: translate what is inside
      const e = core.match(/^([^0-9A-Za-zА-Яа-яЁё]*)([\s\S]*?)([^0-9A-Za-zА-Яа-яЁё]*)$/);
      if (e && (e[1] || e[3]) && e[2]){ const inner = tr(e[2], 0); if (inner !== null) t = e[1] + inner + e[3]; }
    }
    if (t === null) t = piecewise(core);
    return t === null || t === core ? null : m[1] + t + m[3];
  }
  function doNode(n){
    if (done.get(n) === n.nodeValue) return;
    const t = translateText(n.nodeValue);
    if (t !== null){ n.nodeValue = t; }
    done.set(n, n.nodeValue);
  }
  function doEl(el){
    for (const a of ATTRS){ const v = el.getAttribute && el.getAttribute(a); if (v && CYR.test(v)){ const t = translateText(v); if (t !== null) el.setAttribute(a, t); } }
  }
  function walk(root){
    if (!root) return;
    if (root.nodeType === 3){ const p = root.parentNode; if (!p || !SKIP[p.nodeName]) doNode(root); return; }
    if (root.nodeType !== 1 && root.nodeType !== 11) return;
    if (root.nodeType === 1){ if (root.hasAttribute("data-noi18n")) return; doEl(root); if (SKIP[root.nodeName]) return; }
    const it = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: n => { if (n.nodeType !== 1) return NodeFilter.FILTER_ACCEPT; if (n.hasAttribute("data-noi18n")) return NodeFilter.FILTER_REJECT; if (SKIP[n.nodeName]){ doEl(n); return NodeFilter.FILTER_REJECT; } return NodeFilter.FILTER_ACCEPT; }
    });
    let n; while ((n = it.nextNode())){ if (n.nodeType === 3) doNode(n); else doEl(n); }
  }
  function t(s){ if (!ready || lang === "ru") return s; const r = translateText(String(s)); return r === null ? s : r; }

  window.MD_I18N = {
    lang, langs: LANGS, locale: LANGS[lang].locale, t,
    set(code){ if (!LANGS[code]) return; try { localStorage.setItem(KEY, code); } catch (e) {} location.reload(); }
  };
  document.documentElement.lang = lang;
  if (lang === "ru") return;

  const html = document.documentElement;
  html.classList.add("i18n-wait");
  let shown = false;
  const reveal = () => { if (shown) return; shown = true; html.classList.remove("i18n-wait"); };
  setTimeout(reveal, 2500);
  fetch("i18n/" + lang + ".json").then(r => r.ok ? r.json() : Promise.reject(r.status)).then(dict => {
    build(dict); ready = true;
    const start = () => {
      walk(document.body);
      const tt = translateText(document.title); if (tt) document.title = tt;
      // translate everything the app draws later
      new MutationObserver(list => {
        for (const m of list){
          if (m.type === "characterData") { const p = m.target.parentNode; if (p && !SKIP[p.nodeName]) doNode(m.target); }
          else if (m.type === "attributes") { if (CYR.test(m.target.getAttribute(m.attributeName) || "")) doEl(m.target); }
          else m.addedNodes.forEach(walk);
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
      reveal();
    };
    if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
  }).catch(reveal);
})();
