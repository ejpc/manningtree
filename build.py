#!/usr/bin/env python3
"""
Build every Manningtree site from one template.

Every site gets the SAME page: same sections, same order, same components.
Only the data and the colours change. To add a business, add an entry to
SITES and run:  python3 build.py

    index.html   home page
    <sub>.html   menu / services page
"""
import json
import pathlib
import re
from string import Template

HERE = pathlib.Path(__file__).parent
BASE = "https://ejpc.github.io/manningtree"

# --------------------------------------------------------------------------
# The template. One stylesheet, one page shape, for all sites.
# --------------------------------------------------------------------------

CSS = Template("""
  :root{
    --brand:$brand; --brand-dark:$brand_dark; --accent:$accent;
    --page:$page; --ink:$ink; --soft:$soft; --card:$card; --line:$line;
    --panel:$panel; --head:$head; --on-brand:$on_brand; --btn-text:$btn_text;
    --btn-bg:$btn_bg; --btn-fg:$btn_fg;
    --hero-a:$hero_a; --hero-b:$hero_b; --brand-ink:$brand_ink;
    --chip-border:$chip_border; --hero-shade:$hero_shade; --hero-glow:$hero_glow; --chip-bg:$chip_bg; --cta-bg:$cta_bg; --cta-fg:$cta_fg;
  }
  *{ box-sizing:border-box; margin:0; padding:0; }
  html{ scroll-behavior:smooth; }
  body{ font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;
    color:var(--ink); background:var(--page); line-height:1.6; }
  .serif{ font-family:Georgia,'Times New Roman',serif; }
  a:focus-visible, button:focus-visible{ outline:3px solid var(--accent); outline-offset:3px; border-radius:6px; }
  .skip{ position:absolute; left:-9999px; top:0; z-index:100; background:#fff; color:#222;
    padding:12px 20px; border-radius:0 0 10px 0; text-decoration:none; font-weight:bold; }
  .skip:focus{ left:0; }

  header{ position:sticky; top:0; z-index:10; display:flex; justify-content:space-between;
    align-items:center; padding:16px 30px; background:var(--brand); }
  header .logo{ font-family:$logo_font; font-size:calc(23px * $logo_scale); font-weight:$logo_weight;
    letter-spacing:$logo_track; color:var(--brand-ink); line-height:1.1; }
  header .logo small{ display:block; font-family:Georgia,serif; font-size:10px; letter-spacing:4px;
    font-weight:normal; color:var(--accent); }
  header nav a{ color:var(--on-brand); text-decoration:none; margin-left:16px; font-size:14px;
    letter-spacing:1px; text-transform:uppercase; position:relative;
    display:inline-flex; align-items:center; min-height:44px; padding:0 4px; }
  header nav a:hover{ color:var(--brand-ink); }
  header nav a::after{ content:""; position:absolute; left:4px; right:4px; bottom:9px; height:2px;
    background:var(--accent); transform:scaleX(0); transform-origin:left;
    transition:transform .2s ease; }
  header nav a:hover::after{ transform:scaleX(1); }

  .hero{ position:relative; overflow:hidden; color:var(--brand-ink); padding:80px 24px 88px;
    background:linear-gradient(160deg,var(--hero-a) 0%,var(--hero-b) 100%); }
  .hero::before{ content:""; position:absolute; inset:0; pointer-events:none;
    background:radial-gradient(circle at 20% 15%, var(--hero-glow), transparent 55%),
               radial-gradient(circle at 85% 90%, var(--hero-shade), transparent 55%); }
  .hero .art{ position:absolute; pointer-events:none; z-index:0; opacity:$art_opacity; }
  .hero .art-l{ top:-40px; left:-52px; width:$art_l; }
  .hero .art-r{ right:$art_r_right; bottom:$art_r_bottom; width:$art_r; }
  .hero .inner{ position:relative; z-index:1; max-width:880px; margin:0 auto; }
  .hero .inner > *{ position:relative; }
  .hero h1{ font-family:$hero_font; font-size:clamp(36px,9vw,62px); letter-spacing:2px; line-height:1; }
  .hero .place{ display:block; font-size:clamp(12px,2.4vw,15px); letter-spacing:clamp(4px,1.6vw,8px);
    color:var(--accent); margin-top:10px; }
  .hero p{ font-family:Georgia,serif; font-size:clamp(17px,2.6vw,22px); color:var(--on-brand);
    max-width:560px; margin:24px 0 0; font-style:italic; }
  .hero .chips{ margin-top:28px; }
  .hero .chips span{ display:inline-block; margin:6px 8px 6px 0; padding:9px 20px;
    border:1px solid var(--chip-border); border-radius:30px; font-size:14px; letter-spacing:1px; }
  .hero .chips span.status{ display:none; align-items:center; gap:9px; background:var(--chip-bg); }
  .hero .chips span.status.on{ display:inline-flex; }
  .hero .chips span.status .dot{ display:block; flex:0 0 9px; width:9px; height:9px; margin:0;
    padding:0; border:0; border-radius:50%; background:#8ee39c; box-shadow:0 0 0 4px rgba(142,227,156,.22); }
  .hero .chips span.status.shut .dot{ background:#f0a396; box-shadow:0 0 0 4px rgba(240,163,150,.22); }
  .hero .cta{ display:inline-block; margin-top:30px; background:var(--cta-bg); color:var(--cta-fg);
    text-decoration:none; padding:15px 38px; border-radius:40px; font-size:16px; font-weight:bold;
    letter-spacing:1px; box-shadow:0 5px 0 rgba(0,0,0,.28);
    transition:transform .1s ease, box-shadow .1s ease, filter .2s ease; }
  .hero .cta:hover{ filter:brightness(1.08); transform:translateY(-2px); box-shadow:0 7px 0 rgba(0,0,0,.28); }
  .hero .cta:active{ transform:translateY(4px); box-shadow:0 1px 0 rgba(0,0,0,.28); }

  section{ max-width:880px; margin:0 auto; padding:60px 24px; }
  section[id]{ scroll-margin-top:96px; }
  .head{ text-align:center; margin-bottom:34px; }
  .head h2{ font-family:Georgia,serif; font-size:clamp(26px,5.6vw,34px); color:var(--head); }
  .head .deco{ width:60px; height:3px; background:var(--accent); margin:14px auto 0; border-radius:3px; }
  .lead{ text-align:center; font-size:19px; color:var(--soft); max-width:620px; margin:0 auto; }

  .cards{ display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:20px; }
  .cards .item{ background:var(--card); border:1px solid var(--line); border-radius:16px;
    padding:26px 22px; text-align:center; box-shadow:0 4px 14px rgba(0,0,0,.05); transition:transform .15s; }
  .cards .item:hover{ transform:translateY(-4px); }
  .cards .item h3{ font-family:Georgia,serif; color:var(--head); margin-bottom:8px; font-size:21px; }
  .cards .item p{ color:var(--soft); font-size:15px; }

  .center{ text-align:center; margin-top:36px; }
  .btn{ display:inline-block; background:var(--btn-bg); color:var(--btn-fg); font-weight:bold; text-decoration:none;
    padding:15px 38px; border-radius:40px; font-size:16px; letter-spacing:1px;
    box-shadow:0 5px 0 rgba(0,0,0,.35); transition:transform .1s ease, box-shadow .1s ease, filter .2s ease; }
  .btn:hover{ filter:brightness(1.12); transform:translateY(-2px); box-shadow:0 7px 0 rgba(0,0,0,.35); }
  .btn:active{ transform:translateY(4px); box-shadow:0 1px 0 rgba(0,0,0,.35); }

  .btn.ghost{ background:transparent; color:var(--head); border:2px solid var(--accent);
    box-shadow:0 5px 0 rgba(0,0,0,.14); }
  .btn + .btn{ margin-left:12px; }
  @media(max-width:560px){ .btn + .btn{ margin-left:0; margin-top:14px; }
    .center .btn{ display:block; }
  }

  .gallery{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:16px; }
  .gallery figure{ margin:0; border-radius:16px; overflow:hidden; border:1px solid var(--line);
    background:var(--card); box-shadow:0 4px 14px rgba(0,0,0,.06); }
  .gallery img{ display:block; width:100%; height:auto; aspect-ratio:4/3; object-fit:cover;
    transition:transform .45s ease; }
  .gallery figure:hover img{ transform:scale(1.05); }
  .gallery figcaption{ padding:11px 15px; font-family:Georgia,serif; font-style:italic;
    font-size:14px; color:var(--soft); }

  .band{ background:var(--panel); max-width:none; }
  .band .row{ display:flex; flex-wrap:wrap; justify-content:center; gap:14px; }
  .band .row span{ background:var(--card); border:1px solid var(--line); padding:12px 24px;
    border-radius:30px; font-size:16px; color:var(--ink); }

  .hours{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:22px; }
  .hours .card{ background:var(--card); border:1px solid var(--line); border-radius:16px;
    padding:28px; text-align:center; }
  .hours .card h3{ font-family:Georgia,serif; color:var(--head); font-size:20px; margin-bottom:12px; }
  .hours .card p{ color:var(--ink); font-size:16px; margin:4px 0; }
  .hours .card .small{ color:var(--soft); font-size:14px; font-style:italic; }
  .hours .card a, .faq .q a, .rows a, .note a, .lead a{ color:var(--accent);
    font-weight:bold; text-decoration:underline; text-underline-offset:2px; }

  .faq .q{ background:var(--card); border:1px solid var(--line); border-radius:14px;
    padding:20px 24px; margin-bottom:14px; }
  .faq .q h3{ font-family:Georgia,serif; color:var(--head); font-size:18px; margin-bottom:5px; }
  .faq .q p{ color:var(--soft); font-size:16px; }

  .map{ border-radius:16px; overflow:hidden; border:1px solid var(--line); box-shadow:0 4px 14px rgba(0,0,0,.06); }
  .map iframe{ display:block; width:100%; height:340px; border:0; }

  footer{ background:var(--brand-dark); color:var(--on-brand); text-align:center; padding:56px 24px; }
  footer .logo{ font-family:$logo_font; font-size:calc(26px * $logo_scale); font-weight:$logo_weight;
    letter-spacing:$logo_track; color:var(--brand-ink); line-height:1.1; }
  footer .logo small{ display:block; font-family:Georgia,serif; font-size:10px; letter-spacing:4px;
    color:var(--accent); margin-top:4px; }
  footer .info{ font-size:18px; margin:18px 0 6px; font-style:normal; }
  footer a{ color:var(--accent); text-decoration:none; display:inline-block;
    padding:8px 4px; min-height:24px; }
  footer .socials{ margin-top:18px; }
  footer .socials a{ margin:0 6px; padding:11px 8px; font-size:15px; letter-spacing:1px; }

  .call-fab{ position:fixed; right:18px; bottom:18px; z-index:50; background:var(--accent);
    color:var(--btn-text); text-decoration:none; padding:14px 22px; border-radius:40px;
    font-size:15px; font-weight:bold; letter-spacing:.5px; box-shadow:0 6px 18px rgba(0,0,0,.3);
    transition:transform .1s ease, box-shadow .1s ease; }
  .call-fab:hover{ transform:translateY(-2px); box-shadow:0 9px 22px rgba(0,0,0,.36); }
  .call-fab:active{ transform:translateY(2px) scale(.97); box-shadow:0 3px 10px rgba(0,0,0,.3); }

  .reveal{ opacity:0; transform:translateY(16px); transition:opacity .55s ease, transform .55s ease; }
  .reveal.in{ opacity:1; transform:none; }
  @media (prefers-reduced-motion: reduce){
    html{ scroll-behavior:auto; }
    *, *::before, *::after{ animation-duration:.001ms !important; transition-duration:.001ms !important; }
    .reveal{ opacity:1; transform:none; }
  }

  @media(max-width:1040px){ .hero .art{ display:none; } }
  @media(max-width:640px){
    header{ flex-direction:column; gap:9px; padding:13px 18px; text-align:center; }
    header .logo{ font-size:20px; }
    header nav{ display:flex; flex-wrap:wrap; justify-content:center; }
    header nav a{ margin:0 6px; font-size:13px; min-height:44px; }
    section[id]{ scroll-margin-top:124px; }
    section{ padding:46px 20px; }
    .hero{ padding:60px 20px 68px; }
    .hero .chips span{ font-size:13px; padding:8px 16px; }
    .map iframe{ height:280px; }
    footer{ padding:46px 20px 104px; }
    .call-fab{ left:18px; right:18px; bottom:14px; text-align:center; padding:15px 22px; }
    .hero .art{ display:none; }
    .hero .art-l{ width:150px; top:-22px; left:-34px; }
    .hero .art-r{ width:165px; right:-26px; bottom:-34px; }
  }
""")

SCRIPT = Template("""
<script>
(function () {
  'use strict';
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Fade blocks in on scroll. The class is added here, not in the HTML, so
     that with JavaScript switched off nothing is ever hidden. */
  if (!calm && 'IntersectionObserver' in window) {
    var blocks = document.querySelectorAll('section .head, .cards .item, .gallery figure, .hours .card, .faq .q, .map, .band .row span');
    var watcher = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('in');
        watcher.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    blocks.forEach(function (el, i) {
      el.classList.add('reveal');
      el.style.transitionDelay = (i % 6) * 45 + 'ms';
      watcher.observe(el);
    });
  }

  /* "Open now" badge. 0 = Sunday, minutes from midnight, missing day = closed.
     Worked out in UK time so a visitor abroad still sees the right answer. */
  var HOURS = $hours_js;
  var DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  var FULL = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

  var badge = document.getElementById('openStatus');
  if (!badge) return;

  var got = {};
  new Intl.DateTimeFormat('en-GB', { timeZone:'Europe/London', weekday:'short',
    hour:'2-digit', minute:'2-digit', hour12:false })
    .formatToParts(new Date()).forEach(function (p) { got[p.type] = p.value; });

  var day = DAYS.indexOf(got.weekday);
  var now = parseInt(got.hour, 10) * 60 + parseInt(got.minute, 10);
  if (day < 0) return;

  function clock(mins) {
    var h = Math.floor(mins / 60), m = mins % 60;
    return (h % 12 === 0 ? 12 : h % 12) + ':' + (m < 10 ? '0' : '') + m + (h < 12 ? 'am' : 'pm');
  }

  var today = HOURS[day];
  if (today && now >= today[0] && now < today[1]) {
    badge.className = 'status on';
    badge.innerHTML = '<span class="dot"></span>Open now &middot; until ' + clock(today[1]);
    return;
  }

  var when = '';
  if (today && now < today[0]) {
    when = ' &middot; opens ' + clock(today[0]);
  } else {
    for (var ahead = 1; ahead <= 7; ahead++) {
      var next = HOURS[(day + ahead) % 7];
      if (!next) continue;
      when = ' &middot; opens ' + (ahead === 1 ? 'tomorrow' : FULL[(day + ahead) % 7]) + ' ' + clock(next[0]);
      break;
    }
  }
  badge.className = 'status on shut';
  badge.innerHTML = '<span class="dot"></span>Closed' + when;
})();
</script>
""")

PAGE = Template("""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<meta name="description" content="$description">
<link rel="canonical" href="$url">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="$brand">
<meta name="geo.region" content="GB-ESS">
<meta name="geo.placename" content="Manningtree">
<meta name="geo.position" content="$lat;$lon">
<meta name="ICBM" content="$lat, $lon">
<meta name="format-detection" content="telephone=no">

<meta property="og:site_name" content="$name_esc">
<meta property="og:title" content="$og_title">
<meta property="og:description" content="$og_description">
<meta property="og:type" content="$og_type">
<meta property="og:url" content="$url">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="${url}social-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta property="og:image:alt" content="$og_image_alt">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="$og_title">
<meta name="twitter:description" content="$og_description">
<meta name="twitter:image" content="${url}social-card.png">

$font_link<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">

$jsonld
<style>$css</style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>

  <header>
    <div class="logo">$logo<small>$logo_sub</small></div>
    <nav aria-label="Main">
      <a href="$sub_file">$sub_nav</a>
      <a href="#photos">Photos</a>
      <a href="#hours">Hours</a>
      <a href="#faq">FAQ</a>
      <a href="#find">Find Us</a>
    </nav>
  </header>

  <main id="main">
    <div class="hero">
$hero_art      <div class="inner">
        <h1 class="serif">$name</h1>
        <span class="place">$place</span>
        <p>$tagline</p>
        <div class="chips">
          <span class="status" id="openStatus"></span>
$chips
        </div>
        <br>
        <a href="$cta_href"$cta_attrs class="cta">$cta_label</a>
      </div>
    </div>

    <section>
      <div class="head"><h2>$welcome_heading</h2><div class="deco"></div></div>
      <p class="lead">$welcome</p>
    </section>

    <section id="offer">
      <div class="head"><h2>$offer_heading</h2><div class="deco"></div></div>
      <div class="cards">
$cards
      </div>
      <div class="center"><a href="$sub_file" class="btn">$sub_cta</a></div>
    </section>

    <section id="photos">
      <div class="head"><h2>$photos_heading</h2><div class="deco"></div></div>
      <div class="gallery">
$photos
      </div>
    </section>

    <section class="band">
      <div style="max-width:880px; margin:0 auto;">
        <div class="head"><h2>$perks_heading</h2><div class="deco"></div></div>
        <div class="row">
$perks
        </div>
      </div>
    </section>

    <section id="hours">
      <div class="head"><h2>Opening Hours</h2><div class="deco"></div></div>
      <div class="hours">
$hours
      </div>
$hours_extra    </section>

    <section id="faq">
      <div class="head"><h2>Questions &amp; Answers</h2><div class="deco"></div></div>
      <div class="faq">
$faqs
      </div>
    </section>

    <section id="find">
      <div class="head"><h2>Find Us</h2><div class="deco"></div></div>
      <div class="map">
        <iframe src="https://maps.google.com/maps?q=$map_q&output=embed" loading="lazy"
          title="Map showing $name, $address, Manningtree"></iframe>
      </div>
      <div class="center"><a href="$directions" target="_blank" rel="noopener" class="btn">Get Directions</a></div>
    </section>
  </main>

  <footer id="contact">
    <div class="logo">$logo<small>$logo_sub</small></div>
    <address class="info">$address, Manningtree, Essex, $postcode</address>
$phone_line
    <div class="socials">
$socials
    </div>
  </footer>

  <a href="$fab_href"$fab_attrs class="call-fab">$fab_label</a>
$script
</body>
</html>
""")

SUB = Template("""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$sub_title</title>
<meta name="description" content="$sub_description">
<link rel="canonical" href="$sub_url">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="$brand">

<meta property="og:site_name" content="$name_esc">
<meta property="og:title" content="$sub_title">
<meta property="og:description" content="$sub_description">
<meta property="og:type" content="article">
<meta property="og:url" content="$sub_url">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="${url}social-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="$sub_title">
<meta name="twitter:description" content="$sub_description">
<meta name="twitter:image" content="${url}social-card.png">

$font_link<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">

$sub_jsonld
<style>$css
  .rows{ max-width:680px; margin:0 auto; }
  .rows .r{ display:flex; justify-content:space-between; align-items:baseline; gap:16px;
    padding:14px 4px; border-bottom:1px dotted var(--line); }
  .rows .r .n{ display:flex; flex-direction:column; }
  .rows .r .n b{ font-family:Georgia,serif; font-size:18px; color:var(--head); }
  .rows .r .n .d{ font-size:14px; color:var(--soft); font-style:italic; margin-top:2px; }
  .rows .r .p{ color:var(--accent); font-weight:bold; font-size:17px; white-space:nowrap; }
  .sub{ text-align:center; color:var(--soft); font-style:italic; margin:-18px 0 22px; font-size:16px; }
  .note{ max-width:680px; margin:0 auto; padding:22px 24px; color:var(--soft); font-size:14px;
    font-style:italic; text-align:center; }
  .flag{ max-width:680px; margin:0 auto 8px; padding:16px 22px; background:var(--card);
    border:1px solid var(--accent); border-radius:12px; color:var(--soft); font-size:14px;
    font-style:italic; text-align:center; }
</style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>

  <header>
    <div class="logo">$logo<small>$logo_sub</small></div>
    <nav aria-label="Main">
      <a href="index.html">Home</a>
      <a href="index.html#hours">Hours</a>
      <a href="index.html#faq">FAQ</a>
      <a href="index.html#find">Find Us</a>
    </nav>
  </header>

  <main id="main">
    <div class="hero">
$hero_art      <div class="inner" style="text-align:center;">
        <h1 class="serif">$sub_h1</h1>
        <p style="margin-left:auto; margin-right:auto;">$sub_lede</p>
      </div>
    </div>

$flag
$sections
    <p class="note">$sub_note</p>

    <div class="center" style="padding:0 24px 56px;">
      <a href="index.html" class="btn">Back to Home</a>
    </div>
  </main>

  <footer>
    <div class="logo">$logo<small>$logo_sub</small></div>
    <address class="info">$address, Manningtree, Essex, $postcode</address>
$phone_line
  </footer>

  <a href="$fab_href"$fab_attrs class="call-fab">$fab_label</a>
</body>
</html>
""")

# --------------------------------------------------------------------------
# The data. One entry per business. Everything below is verified - see the
# notes against the hours and prices for where each figure came from.
# --------------------------------------------------------------------------

SITES = {

"hobsons": dict(
  name="Hobsons", name_plain="Hobson's Deli & Café",
  logo="Hobsons", logo_sub="DELI &amp; CAFÉ", place="DELI &amp; CAFÉ &middot; MANNINGTREE",
  # charcoal brush-script logo on kraft paper, taken from their own printed menu
  brand="#333d44", brand_dark="#232b30", accent="#6f8b9b", page="#f3f5f6",
  ink="#263036", soft="#5d6b74", card="#ffffff", line="#dde4e8", panel="#e6ecef",
  head="#333d44", on_brand="#cbd6dd", btn_text="#1d252a",
  hero_a="#46535b", hero_b="#262f35", btn_bg="#333d44", btn_fg="#ffffff",
  title="Hobson's Deli &amp; Café Manningtree | Deli Counter, Cheese, Breakfast &amp; Coffee",
  description="Hobson's Deli &amp; Café on Manningtree High Street. Homemade sausage rolls, quiches and scones, a proper cheese counter, breakfast, jacket potatoes, toasties and coffee. Family run and dog friendly. 21 High Street, Manningtree CO11 1AG.",
  og_title="Hobson's Deli &amp; Café Manningtree | Deli Counter &amp; Coffee",
  og_description="Homemade deli counter, cheeses, breakfast, lunch and proper coffee in the heart of Manningtree. Family run, dog friendly.",
  og_type="restaurant.restaurant",
  og_image_alt="Hobson's Deli and Café, Manningtree - deli counter, cheeses, breakfast and coffee",
  tagline="A family-run deli and café in the heart of the smallest town in England &mdash; everything homemade.",
  chips=["Deli counter", "Cheese selection", "Dog friendly"],
  cta_label="See the Menu", cta_href="menu.html", cta_attrs="",
  welcome_heading="Welcome to Hobson's",
  welcome="Tucked along Manningtree High Street, Hobson's is part deli, part café &mdash; and proudly family run. Browse the counter for homemade sausage rolls, quiches and a proper cheese selection, or pull up a chair for breakfast, lunch and a good coffee. Everything is made from scratch, and well-behaved dogs are always welcome.",
  offer_heading="What We Serve",
  cards=[("Breakfast", "Bacon, sausage or fried egg in a sandwich or ciabatta &mdash; veggie available"),
         ("Lunch &amp; Toasties", "Ciabattas, ploughman's, toasties and loaded jacket potatoes"),
         ("The Deli Counter", "Cheeses, Suffolk ham, cured meats and Mrs Darlington's preserves"),
         ("Homemade Scones", "Fruit, cheese and hot cross bun scones, baked in-house daily"),
         ("Sausage Rolls &amp; Quiches", "Made here, alongside cakes and savoury pastries"),
         ("Coffee, Frappes &amp; Shakes", "Flavoured lattes, iced frappes and milkshakes")],
  photos_heading="A Look Inside",
  photos=[("deli-counter", "The deli counter"), ("ploughmans", "Our ploughman's"),
          ("cheese-selection", "A few from the cheese counter"),
          ("homemade-scones", "Homemade fruit &amp; cheese scones"),
          ("preserves", "Jams, curds &amp; chutneys to take home"),
          ("inside-the-cafe", "Inside Hobson's")],
  perks_heading="Why Pop In",
  perks=["5&#9733; food hygiene rating", "Family run", "Everything homemade",
         "Deli counter to take home", "Indoor &amp; covered outdoor seating",
         "Dog friendly", "Vegetarian &amp; vegan options", "Eat in or takeaway",
         "Wheelchair accessible"],
  # Google Business Profile, confirmed against Restaurantji and Restaurant Guru
  hours=[("Deli &amp; Café", ["Tue &ndash; Sat: 9:00am &ndash; 3:00pm"], "Closed Sunday &amp; Monday"),
         ("Breakfast", ["Served 9:00am &ndash; 12:00 noon"], "Lunch served through the afternoon")],
  hours_js={2:[540,900], 3:[540,900], 4:[540,900], 5:[540,900], 6:[540,900]},
  hours_spec=[(["Tuesday","Wednesday","Thursday","Friday","Saturday"], "09:00", "15:00")],
  faqs=[("Do I need to book a table?", "No need &mdash; just pop in. For larger groups, give us a ring on 01206 395071 and we'll do our best to save you a spot."),
        ("Are dogs allowed?", "Yes! Well-behaved dogs are very welcome &mdash; and there are usually treats on hand."),
        ("Can I buy from the deli to take home?", "Of course. Our counter has cheeses, cured meats, sausage rolls, quiches, jams and chutneys to take away."),
        ("Do you do takeaway?", "Yes &mdash; everything is available to eat in or take away, and there's a meal deal on sandwiches. We don't offer delivery."),
        ("Do you cater for vegetarians?", "We do &mdash; there are vegetarian and vegan choices and daily specials. Please tell us about any allergies as we're a small kitchen."),
        ("Is there outdoor seating?", "Yes &mdash; there's seating inside and a covered outdoor area."),
        ("What are your opening hours?", "Tuesday to Saturday, 9:00am &ndash; 3:00pm. Closed Sunday and Monday.")],
  address="21 High Street", postcode="CO11 1AG",
  phone="01206 395071", phone_intl="+441206395071",
  socials=[("Facebook", "https://www.facebook.com/hobsonsdelicafe/")],
  map_q="Hobson's%20Deli%20Cafe%2021%20High%20Street%20Manningtree%20CO11%201AG",
  directions="https://www.google.com/maps/dir/?api=1&destination=Hobson%27s+Deli+Cafe+21+High+Street+Manningtree+CO11+1AG",
  fab_label="Call Us", fab_href="tel:01206395071", fab_attrs="",
  schema_type="CafeOrCoffeeShop", cuisine=["Deli","Cafe","Breakfast","British"], price_range="££",
  amenities=["Food hygiene rating 5 out of 5","Dog friendly","Covered outdoor seating",
             "Deli counter to take home","Family run","Vegetarian and vegan options",
             "Wheelchair accessible","Table service","Dine-in","Takeaway"],
  reservations="False",
  sub_file="menu.html", sub_nav="Menu", sub_cta="See the Full Menu", sub_kind="menu",
  sub_h1="Our Menu", sub_lede="Everything homemade &middot; deli counter &amp; café kitchen",
  sub_title="Menu &mdash; Hobson's Deli &amp; Café Manningtree",
  sub_description="The menu at Hobson's Deli &amp; Café, 21 High Street, Manningtree. Breakfast baps, ciabattas, toasties, jacket potatoes, homemade scones, the deli counter and proper coffee.",
  # the only priced copy we have is the 2020 TAKEAWAY menu, so no prices are shown
  sub_flag="<b>Hobson's &mdash; prices to add.</b> These dishes are taken from Hobson's own printed menu. Prices aren't shown yet because the only copy we have is the <i>takeaway</i> menu from 2020, and eat-in prices differ. Send your current list and we'll add it &mdash; the page is built and ready for them.",
  sub_note="Everything is made fresh and to order. Please tell us of any allergies, intolerances or dietary requirements &mdash; we're a small kitchen and cannot guarantee against allergen cross-contamination.",
  sub_sections=[
    ("Breakfast", "Extra fillings available", [
      ("Bacon Sandwich or Ciabatta", "", ""), ("Sausage Sandwich or Ciabatta", "veggie available", ""),
      ("Fried Egg Sandwich or Ciabatta", "", "")]),
    ("Sandwiches &amp; Ciabattas", "", [
      ("Cheese &amp; Pickle", "", ""), ("Ham &amp; Mustard", "", ""), ("Tuna Mayo", "", ""),
      ("Ploughman's", "cheese, pickle, ham &amp; tomato", ""), ("Prawn Mayo", "", "")]),
    ("Toasted Sandwiches", "", [
      ("Ham &amp; Cheese", "", ""), ("Tuna, Red Onion &amp; Cheddar", "", ""),
      ("Brie &amp; Cranberry", "", ""), ("Cheese &amp; Onion or Tomato", "", "")]),
    ("Jacket Potatoes", "", [
      ("Cheese &amp; Beans", "", ""), ("Cheese, Beans &amp; Bacon", "", ""),
      ("Tuna Mayo &amp; Cheese", "", ""), ("Prawn Mayo", "", "")]),
    ("Meal Deal", "", [
      ("Sandwich or Ciabatta, Crisps &amp; a Drink", "takeaway &middot; with an americano, tea or a can", "")]),
    ("Homemade Scones, Cakes &amp; Bakes", "Ask what's on the board today", [
      ("Fruit Scone", "", ""), ("Cheese Scone", "", ""), ("Hot Cross Bun Scone", "", ""),
      ("Sausage Rolls &amp; Quiches", "", ""), ("Cake of the Day", "", "")]),
    ("Coffee &amp; Hot Drinks", "Soya milk available", [
      ("Americano", "", ""), ("Cappuccino", "", ""), ("Latte", "", ""), ("Espresso", "single or double", ""),
      ("Mocha", "", ""), ("Hot Chocolate", "", ""), ("Hot Chocolate Supreme", "", ""),
      ("Tea or Herbal Tea", "", ""),
      ("Flavoured Lattes", "pumpkin spice, caramel, vanilla, gingerbread", "")]),
    ("Cold Drinks", "", [
      ("Frappes", "plain, caramel, vanilla or chocolate iced coffee", ""),
      ("Milkshakes", "strawberry, chocolate or vanilla", ""),
      ("Apple or Orange Juice", "", ""), ("Folkingtons", "", ""),
      ("Coke, Diet Coke, 7up or Fanta", "cans", ""), ("Bottled Water", "", "")]),
    ("From the Deli Counter", "To take home", [
      ("Cheese Selection", "ask for a sample &amp; a recommendation", ""),
      ("Cured Meats &amp; Suffolk Ham", "sliced to order", ""),
      ("Mrs Darlington's Jams, Curds &amp; Marmalades", "", ""),
      ("Chutneys, Pickles &amp; Relishes", "", "")]),
  ],
  brand_ink="#ffffff",
  chip_border="rgba(255,255,255,.40)",
  chip_bg="rgba(255,255,255,.12)",
  hero_shade="rgba(0,0,0,.24)",
  logo_font="'Kaushan Script',Georgia,cursive",
  logo_track="0",
  logo_scale="1.4",
  logo_weight="400",
  hero_art="",
  font_link='''<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Kaushan+Script&display=swap">
''',
  hero_font="'Kaushan Script',Georgia,cursive",
  cta_bg="#ffffff",
  cta_fg="#263036",
  hero_glow="rgba(255,255,255,.10)",
  art_l="270px",
  art_r="290px",
  art_r_right="-36px",
  art_r_bottom="-56px",
  art_opacity=".42",
  hours_extra="",
  lat="51.945495", lon="1.063604",
),
}

SITES["rileys"] = dict(
  name="Rileys Barbers", name_plain="Rileys Barbers",
  logo="RILEYS", logo_sub="BARBERS &middot; MANNINGTREE", place="MANNINGTREE",
  # the shop itself is red brick, mahogany and oxblood leather
  brand="#171514", brand_dark="#0f0e0d", accent="#c8a24a", page="#171514",
  ink="#f3efe6", soft="#d6cdc6", card="#221e1c", line="#362e2a", panel="#241a17",
  head="#c8a24a", on_brand="#d6cdc6", btn_text="#0f0e0d",
  hero_a="#241a18", hero_b="#241a18", btn_bg="#c8a24a", btn_fg="#0f0e0d",
  title="Rileys Barbers Manningtree | Cuts, Skin Fades &amp; Beard Trims",
  description="Rileys Barbers, 49 High Street, Manningtree. Classic and modern men's cuts, skin fades, beard trims, kids and senior cuts from £15. Book online or walk in. CO11 1AH.",
  og_title="Rileys Barbers Manningtree | Cuts, Fades &amp; Beard Trims",
  og_description="Classic and modern men's cuts, skin fades and beard trims in the heart of Manningtree. Book online or walk in.",
  og_type="business.business",
  og_image_alt="Rileys Barbers, Manningtree - cuts, skin fades and beard trims",
  tagline="Classic and modern men's cuts in the heart of Manningtree &mdash; sharp fades, clean beard trims and a proper chair.",
  chips=["Book online", "Skin fades", "Beard trims"],
  cta_label="Book an Appointment",
  cta_href="https://www.fresha.com/a/rileys-barbers-manningtree-49-high-street-qg6jnoml/booking",
  cta_attrs=' target="_blank" rel="noopener"',
  welcome_heading="Welcome to Rileys",
  welcome="Right on Manningtree High Street, Rileys is the local barbershop for a sharp, well-finished cut. From precision scissor work and skin fades to clean beard trims and the kids' first chair, our barbers take the time to get it right &mdash; in a proper old-school shop of brick, mahogany and leather chairs. Book online in seconds or pop in and take a seat.",
  offer_heading="Our Services",
  cards=[("Standard Haircut", "Classic cut, clipper or scissor finish &middot; &pound;18"),
         ("Fade Haircut", "Skin fade blended into your style &middot; &pound;20"),
         ("Restyle", "A fresh new look, start to finish &middot; &pound;21"),
         ("Wash, Cut &amp; Blow Dry", "The full treatment &middot; &pound;26"),
         ("Beard Trim", "Shaped and tidied &middot; from &pound;7"),
         ("Kids &amp; Seniors", "Boys aged 5&ndash;10 and over 67s &middot; &pound;16")],
  photos_heading="The Shop",
  photos=[("the-shop", "The shop on the High Street"),
          ("barber-chairs", "Proper leather barber chairs"),
          ("a-fresh-fade", "A fresh skin fade"),
          ("beard-trim", "Beard trim, shaped &amp; tidied")],
  perks_heading="Why Choose Rileys",
  perks=["Easy online booking", "Skilled barbers", "Fair, clear pricing",
         "Traditional barber chairs", "Friendly welcome", "Right on the High Street"],
  # Fresha, confirmed against their Google Business Profile
  hours=[("Tuesday &ndash; Friday", ["Tue &ndash; Thu: 8:30am &ndash; 5:30pm", "Fri: 8:30am &ndash; 6:00pm"],
          "Last cut shortly before close"),
         ("Weekend &amp; Monday", ["Sat: 8:30am &ndash; 4:30pm", "Sun: Closed", "Mon: Closed"], "")],
  hours_js={2:[510,1050], 3:[510,1050], 4:[510,1050], 5:[510,1080], 6:[510,990]},
  hours_spec=[(["Tuesday","Wednesday","Thursday"], "08:30", "17:30"),
              (["Friday"], "08:30", "18:00"),
              (["Saturday"], "08:30", "16:30")],
  faqs=[("Do I need to book?", "You can book online through our Fresha page for a time that suits you, or pop in and we'll fit you in when we can."),
        ("Do you cut children's hair?", "Yes &mdash; we cut boys aged 5 to 10, and there's a kids' price of &pound;16."),
        ("Is there a senior citizen price?", "Yes, there's a special price of &pound;16 for over 67s."),
        ("Do you do beard trims?", "We do &mdash; beard trims start from &pound;7, shaped and tidied to suit you."),
        ("What are your opening hours?", "Tuesday to Thursday 8:30am &ndash; 5:30pm, Friday 8:30am &ndash; 6:00pm, Saturday 8:30am &ndash; 4:30pm. Closed Sunday and Monday."),
        ("Where are you?", "49 High Street, right in the centre of Manningtree. See the map below for directions.")],
  address="49 High Street", postcode="CO11 1AH",
  phone="01206 392802", phone_intl="+441206392802",
  socials=[("Facebook", "https://www.facebook.com/RileysBarbers/"),
           ("Book on Fresha", "https://www.fresha.com/a/rileys-barbers-manningtree-49-high-street-qg6jnoml/booking")],
  map_q="Rileys%20Barbers%2049%20High%20Street%20Manningtree%20CO11%201AH",
  directions="https://www.google.com/maps/dir/?api=1&destination=Rileys+Barbers+49+High+Street+Manningtree+CO11+1AH",
  fab_label="Call Us", fab_href="tel:01206392802", fab_attrs="",
  schema_type="HairSalon", cuisine=None, price_range="££",
  amenities=None, reservations=None,
  booking="https://www.fresha.com/a/rileys-barbers-manningtree-49-high-street-qg6jnoml/booking",
  sub_file="services.html", sub_nav="Services", sub_cta="See All Services", sub_kind="services",
  sub_h1="Services &amp; Prices", sub_lede="Book online or walk in &middot; 49 High Street, Manningtree",
  sub_title="Services &amp; Prices &mdash; Rileys Barbers Manningtree",
  sub_description="Services and prices at Rileys Barbers, 49 High Street, Manningtree. Haircuts from £15, skin fades £20, beard trims from £7, kids and senior cuts £16.",
  sub_flag="",
  sub_note="Prices shown are a guide and may change &mdash; please check when you book. Book online through our Fresha page or pop in to the shop on the High Street.",
  sub_sections=[
    ("Haircuts", "", [
      ("Standard Haircut", "classic cut, clipper or scissor finish &middot; approx 30 min", "&pound;18"),
      ("Fade Haircut", "skin fade blended into your style &middot; approx 45 min", "&pound;20"),
      ("Restyle", "a fresh new look, start to finish &middot; approx 45 min", "&pound;21"),
      ("Wash, Cut &amp; Blow Dry", "the full treatment &middot; approx 1 hr", "&pound;26"),
      ("Buzz Cut", "clippers only, one length &middot; approx 30 min", "&pound;15")]),
    ("Beards", "", [
      ("Beard Trim", "shaped and tidied &middot; approx 15 min", "from &pound;7")]),
    ("Kids &amp; Seniors", "", [
      ("Boys Haircut", "ages 5&ndash;10 &middot; approx 30 min", "&pound;16"),
      ("Senior Citizens Haircut", "over 67s &middot; approx 30 min", "&pound;16")]),
  ],
  services_catalog=[("Standard Haircut","18"),("Fade Haircut","20"),("Restyle","21"),
                    ("Wash, Cut & Blow Dry","26"),("Buzz Cut","15"),("Beard Trim","7"),
                    ("Boys Haircut (ages 5-10)","16"),("Senior Citizens Haircut (over 67s)","16")],
  brand_ink="#ffffff",
  chip_border="rgba(255,255,255,.40)",
  chip_bg="rgba(255,255,255,.12)",
  hero_shade="transparent",
  logo_font="Georgia,serif",
  logo_track="2px",
  logo_scale="1",
  logo_weight="bold",
  hero_art="",
  font_link="",
  hero_font="Georgia,'Times New Roman',serif",
  cta_bg="#c8a24a",
  cta_fg="#0f0e0d",
  hero_glow="transparent",
  art_l="330px",
  art_r="440px",
  art_r_right="-150px",
  art_r_bottom="10px",
  art_opacity=".85",
  hours_extra="",
  lat="51.945511", lon="1.065458",
)

SITES["penelopes"] = dict(
  name="Penelope's", name_plain="Penelope's Cafe",
  logo="PENELOPE'S", logo_sub="MANNINGTREE", place="CAFE &middot; MANNINGTREE",
  # deep plum and lilac, taken from their own menu artwork
  brand="#e5dcf1", brand_dark="#cdbee5", accent="#7d63ab", page="#fcfaff",
  ink="#463b5e", soft="#6c6088", card="#ffffff", line="#ece4f6", panel="#f4eefb",
  head="#5a4a7a", on_brand="#55476f", btn_text="#ffffff",
  hero_a="#f2ecfa", hero_b="#ddd0ef", btn_bg="#7d63ab", btn_fg="#ffffff",
  title="Penelope's Cafe Manningtree | Breakfast, Sandwiches &amp; Afternoon Tea",
  description="Penelope's is a friendly little cafe on Stour Street in Manningtree, Essex. Breakfast from £3, fresh sandwiches, full afternoon tea £25, homemade cakes and proper coffee. 21 Stour Street, Manningtree CO11 1DH.",
  og_title="Penelope's Cafe Manningtree | Breakfast, Sandwiches &amp; Afternoon Tea",
  og_description="Breakfast, fresh sandwiches, afternoon tea, homemade cakes and proper coffee in the heart of Manningtree.",
  og_type="restaurant.restaurant",
  og_image_alt="Penelope's Cafe, Manningtree - breakfast, sandwiches and afternoon tea",
  tagline="A friendly little cafe on Stour Street &mdash; breakfast, fresh sandwiches, afternoon tea &amp; proper coffee.",
  chips=["Breakfast &amp; sandwiches", "Afternoon tea", "Homemade cakes"],
  cta_label="See the Menu", cta_href="menu.html", cta_attrs="",
  welcome_heading="Welcome to Penelope's",
  welcome="Tucked away on Stour Street in the heart of Manningtree, Penelope's is the warm, welcoming spot for a fresh breakfast, a proper sandwich, a slice of homemade cake and a really good cup of coffee &mdash; and a full afternoon tea if you book ahead. Pop in, take a seat, and let us look after you.",
  offer_heading="What We Serve",
  cards=[("Breakfast", "Bacon, sausage or egg baps, avocado with poached eggs, smoked salmon with scrambled eggs"),
         ("Sandwiches", "Prawn marie rose, coronation chicken, smashed avocado, cheese or ham with chutney"),
         ("Dish of the Month", "A changing special &mdash; ask what's on today"),
         ("Afternoon Tea", "Finger sandwiches, macaron, cake &amp; choux, scone with jam &amp; cream &middot; &pound;25 &middot; booking needed"),
         ("Cakes &amp; Scones", "A counter of homemade cakes and scones, changing through the week"),
         ("Coffee &amp; Tea", "Proper coffee, loose leaf tea and Hotel Chocolat hot chocolate")],
  photos_heading="A Look Inside",
  photos=[("avocado-poached-eggs", "Avocado &amp; poached eggs on sourdough"),
          ("afternoon-tea", "The full afternoon tea"),
          ("cakes-counter", "Cakes &amp; scones on the counter"),
          ("inside-the-cafe", "Inside Penelope's")],
  perks_heading="Why Pop In",
  perks=["5&#9733; food hygiene rating", "Freshly baked cakes", "Friendly welcome",
         "Made fresh to order", "Right in the town centre", "Dine in or takeaway",
         "Independent &amp; local"],
  # Google Business Profile
  hours=[("Monday &ndash; Friday", ["Mon: 9:00am &ndash; 2:30pm", "Tue &ndash; Fri: 9:00am &ndash; 4:00pm"],
          "Breakfast 9:00 &ndash; 12:00 &middot; sandwiches 12:00 &ndash; 3:00"),
         ("Weekend", ["Saturday: 8:30am &ndash; 3:00pm", "Sunday: Closed"],
          "Afternoon tea 1:30 &ndash; 3:00 &middot; <a href=\"tel:01206970654\">ring 01206 970654 to book</a>")],
  hours_js={1:[540,870], 2:[540,960], 3:[540,960], 4:[540,960], 5:[540,960], 6:[510,900]},
  hours_spec=[(["Monday"], "09:00", "14:30"),
              (["Tuesday","Wednesday","Thursday","Friday"], "09:00", "16:00"),
              (["Saturday"], "08:30", "15:00")],
  faqs=[("Do I need to book?", "Not for breakfast, sandwiches or cake &mdash; just pop in. Afternoon tea is bookings only, so please <a href=\"tel:01206970654\">ring us on 01206 970654</a>."),
        ("Do you make your own cakes?", "We do! Our homemade cakes and bakes are made fresh, and the counter changes through the week."),
        ("Can I take food away?", "Yes &mdash; you can eat in or take away. We don't do delivery."),
        ("Do you do special orders or catering?", "Give us a ring on 01206 970654 or message us on social media to ask about occasion cakes and larger orders."),
        ("What are your opening hours?", "Monday 9:00am &ndash; 2:30pm, Tuesday to Friday 9:00am &ndash; 4:00pm, Saturday 8:30am &ndash; 3:00pm. Closed Sunday."),
        ("Where are you?", "We're at 21 Stour Street, Manningtree, Essex, CO11 1DH &mdash; right in the heart of town.")],
  address="21 Stour Street", postcode="CO11 1DH",
  phone="01206 970654", phone_intl="+441206970654",
  socials=[("Instagram", "https://www.instagram.com/penelopescafe_manningtree/"),
           ("Facebook", "https://www.facebook.com/p/Penelopes-cafe-61568973090160/")],
  map_q="21%20Stour%20Street%20Manningtree%20CO11%201DH",
  directions="https://www.google.com/maps/dir/?api=1&destination=21+Stour+Street+Manningtree+CO11+1DH",
  fab_label="Call Us", fab_href="tel:01206970654", fab_attrs="",
  schema_type="CafeOrCoffeeShop", cuisine=["Cafe","Breakfast","Afternoon Tea","British"],
  price_range="££",
  amenities=["Food hygiene rating 5 out of 5","Homemade cakes","Dine-in","Takeaway",
             "Afternoon tea (booking required)","Independent and local"],
  reservations="True",
  sub_file="menu.html", sub_nav="Menu", sub_cta="See the Full Menu", sub_kind="menu",
  sub_h1="Our Menu", sub_lede="August 2026 &middot; made fresh to order",
  sub_title="Menu &amp; Prices &mdash; Penelope's Cafe Manningtree",
  sub_description="The menu at Penelope's Cafe, 21 Stour Street, Manningtree. Breakfast from £3, sandwiches from £8, full afternoon tea £25, proper coffee and loose leaf tea.",
  sub_flag="",
  sub_note="A selection of cakes and scones is always available &mdash; please see the specials board for more dishes.<br><br><b>Allergen key</b> &mdash; F: Fish &middot; G: Gluten &middot; E: Eggs &middot; N: Nuts &middot; C: Celery &middot; Mu: Mustard &middot; S: Sulphite &middot; M: Milk &middot; So: Soya &middot; Se: Sesame seeds &middot; Mo: Molluscs &middot; Cs: Crustaceans &middot; P: Peanuts &middot; L: Lupin. Please tell us about any allergies before ordering.",
  sub_sections=[
    ("Breakfast", "Served 9:00 &ndash; 12:00 &middot; add bacon &pound;3.50, smoked salmon &pound;3.75, avocado &pound;1.50", [
      ("Bacon Bap", "G, E, M", "&pound;4.50"), ("Sausage Bap", "G, E, M", "&pound;5.00"),
      ("Egg Bap", "G, E, M", "&pound;3.00"),
      ("Avocado with Poached Eggs", "on sourdough toast &middot; G, E, M", "&pound;8.00"),
      ("Smoked Salmon with Scrambled Eggs", "on toast &middot; G, E, M, F", "&pound;8.75")]),
    ("Sandwiches", "Served 12:00 &ndash; 15:00 &middot; all with crisps &amp; salad &middot; white or brown bread", [
      ("Prawn Marie Rose", "G, E, M, Cs", "&pound;9.50"),
      ("Coronation Chicken", "G, E, M", "&pound;8.75"),
      ("Cheese or Ham with Chutney", "G, C, Se", "&pound;8.50"),
      ("Smashed Avocado, Red Onion &amp; Sun-Dried Tomatoes", "G, M", "&pound;8.00")]),
    ("Dish of the Month", "Changes every month &mdash; ask what's on today", [
      ("Smoked Mackerel Pate", "with sourdough toast &amp; salad &middot; G, M, F", "&pound;11.50")]),
    ("Afternoon Tea", "Served 13:30 &ndash; 15:00 &middot; bookings only &middot; <a href=\"tel:01206970654\">ring 01206 970654 to book</a>", [
      ("Full Afternoon Tea", "finger sandwiches &middot; macaron, layered cake &amp; choux &middot; scone, jam &amp; cream &middot; mini sausage roll &middot; any hot or cold drink &middot; G, E, M, N, F, Se", "&pound;25.00")]),
    ("Coffee", "", [
      ("Americano", "M", "&pound;2.80"), ("Cappuccino", "M", "&pound;3.50"),
      ("Flat White", "M", "&pound;3.50"), ("Latte", "M", "&pound;3.50"),
      ("Single Espresso", "", "&pound;2.20"), ("Double Espresso", "", "&pound;2.50")]),
    ("Loose Leaf Tea", "", [
      ("Pot of Tea for 1", "M", "&pound;2.50"), ("Pot of Tea for 2", "M", "&pound;4.00"),
      ("Pot of Speciality Tea", "mixed berry, earl grey or mint", "&pound;3.00")]),
    ("Hotel Chocolat Hot Chocolate", "", [
      ("Milky 50% or Classic 70%", "M", "&pound;4.00"),
      ("Add Cream &amp; Marshmallows", "M", "&pound;0.50"), ("Soya Milk", "So", "&pound;0.40")]),
    ("Cold Drinks", "", [
      ("Fentimans Cola", "", "&pound;3.50"), ("Fentimans Victorian Lemonade", "", "&pound;3.50"),
      ("Appletiser", "", "&pound;3.50"), ("Diet Coke", "", "&pound;3.00"),
      ("Sparkling Water", "", "&pound;2.50"), ("Still Water", "", "&pound;2.00"),
      ("Glass of Orange Juice", "", "&pound;2.00")]),
  ],
  brand_ink="#4b3f66",
  chip_border="rgba(90,70,130,.30)",
  chip_bg="rgba(255,255,255,.62)",
  hero_shade="rgba(140,110,180,.14)",
  logo_font="Georgia,serif",
  logo_track="2px",
  logo_scale="1",
  logo_weight="bold",
  hero_art="""      <img class="art art-l" src="art/flowers-left.png" alt="" aria-hidden="true">
      <img class="art art-r" src="art/flowers-right.png" alt="" aria-hidden="true">
""",
  font_link="",
  hero_font="Georgia,'Times New Roman',serif",
  cta_bg="#7d63ab",
  cta_fg="#ffffff",
  hero_glow="rgba(255,255,255,.10)",
  art_l="300px",
  art_r="330px",
  art_r_right="-36px",
  art_r_bottom="-56px",
  art_opacity=".42",
  hours_extra="""      <div class="center">
        <a href="tel:01206970654" class="btn">Call 01206 970654</a>
        <a href="https://www.instagram.com/penelopescafe_manningtree/" target="_blank"
           rel="noopener" class="btn ghost">Message on Instagram</a>
      </div>
""",
  lat="51.944888", lon="1.062615",
)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

DAY_NAMES = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]


def strip(s):
    """HTML entities out, for use inside JSON-LD strings."""
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in [("&amp;","&"), ("&mdash;"," - "), ("&ndash;","-"), ("&middot;","-"),
                 ("&pound;","£"), ("&#9733;","*")]:
        s = s.replace(a, b)
    return " ".join(s.split())


def business_schema(slug, s, url):
    node = {
      "@context": "https://schema.org",
      "@type": s["schema_type"],
      "@id": url + "#business",
      "name": strip(s["name_plain"]),
      "description": strip(s["welcome"]),
      "url": url,
      "image": url + "social-card.png",
      "hasMap": s["directions"],
      "address": {"@type": "PostalAddress", "streetAddress": s["address"],
                  "addressLocality": "Manningtree", "addressRegion": "Essex",
                  "postalCode": s["postcode"], "addressCountry": "GB"},
      "telephone": s["phone_intl"],
      "geo": {"@type": "GeoCoordinates",
              "latitude": s["lat"], "longitude": s["lon"]},
      "priceRange": s["price_range"],
      "currenciesAccepted": "GBP",
      "paymentAccepted": "Cash, Credit Card, Debit Card, Contactless",
      "areaServed": [{"@type": "Place", "name": n} for n in
                     ["Manningtree", "Mistley", "Lawford", "Tendring, Essex"]],
      "openingHoursSpecification": [
          {"@type": "OpeningHoursSpecification", "dayOfWeek": days,
           "opens": o, "closes": c} for days, o, c in s["hours_spec"]],
      "sameAs": [u for _, u in s["socials"]],
    }
    if s.get("cuisine"):
        node["servesCuisine"] = s["cuisine"]
    if s.get("amenities"):
        node["amenityFeature"] = [
            {"@type": "LocationFeatureSpecification", "name": a, "value": True}
            for a in s["amenities"]]
    if s.get("reservations"):
        node["acceptsReservations"] = s["reservations"]
    if s["sub_kind"] == "menu":
        node["hasMenu"] = {"@type": "Menu", "@id": url + s["sub_file"] + "#menu",
                           "url": url + s["sub_file"], "name": strip(s["name_plain"]) + " Menu"}
    if s.get("services_catalog"):
        node["hasOfferCatalog"] = {
            "@type": "OfferCatalog", "name": "Haircuts & Grooming",
            "itemListElement": [
                {"@type": "Offer", "price": p, "priceCurrency": "GBP",
                 "itemOffered": {"@type": "Service", "name": n}}
                for n, p in s["services_catalog"]]}
    if s.get("booking"):
        node["potentialAction"] = {
            "@type": "ReserveAction",
            "target": {"@type": "EntryPoint", "urlTemplate": s["booking"],
                       "actionPlatform": ["https://schema.org/DesktopWebPlatform",
                                          "https://schema.org/MobileWebPlatform"]},
            "result": {"@type": "Reservation", "name": "Appointment"}}
    return node


def faq_schema(s, url):
    return {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [{"@type": "Question", "name": strip(q),
                            "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
                           for q, a in s["faqs"]]}


def sub_schema(s, url, sub_url):
    if s["sub_kind"] == "menu":
        sections = []
        for heading, _, rows in s["sub_sections"]:
            items = []
            for n, d, price in rows:
                it = {"@type": "MenuItem", "name": strip(n)}
                if d:
                    it["description"] = strip(d)
                amount = strip(price).replace("£", "").strip()
                # only a clean number becomes an Offer - never a guess or a dash
                if amount.replace(".", "", 1).isdigit():
                    it["offers"] = {"@type": "Offer", "price": amount, "priceCurrency": "GBP"}
                items.append(it)
            sections.append({"@type": "MenuSection", "name": strip(heading), "hasMenuItem": items})
        node = {"@context": "https://schema.org", "@type": "Menu", "@id": sub_url + "#menu",
                "url": sub_url, "name": strip(s["name_plain"]) + " Menu",
                "inLanguage": "en-GB", "hasMenuSection": sections}
    else:
        node = {"@context": "https://schema.org", "@type": "WebPage", "@id": sub_url + "#page",
                "url": sub_url, "name": strip(s["sub_title"]), "inLanguage": "en-GB",
                "about": {"@id": url + "#business"},
                "primaryImageOfPage": url + "social-card.png"}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList",
              "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": strip(s["name_plain"]), "item": url},
                  {"@type": "ListItem", "position": 2, "name": strip(s["sub_nav"]), "item": sub_url}]}
    return [node, crumbs]


def ld(nodes):
    return "\n".join('<script type="application/ld+json">\n'
                     + json.dumps(n, indent=2, ensure_ascii=False) + '\n</script>\n'
                     for n in nodes)


def build(slug, s):
    out = HERE / slug
    out.mkdir(exist_ok=True)
    url = f"{BASE}/{slug}/"
    sub_url = url + s["sub_file"]

    css = CSS.substitute(s)
    common = dict(s, css=css, url=url, sub_url=sub_url,
                  name_esc=s["name_plain"].replace("&", "&amp;"))

    phone_line = (f'    <p class="info">Call: <a href="tel:{s["phone"].replace(" ", "")}">'
                  f'{s["phone"]}</a></p>' if s.get("phone") else "")

    (out / "index.html").write_text(PAGE.substitute(
        common,
        jsonld=ld([business_schema(slug, s, url), faq_schema(s, url),
                   {"@context": "https://schema.org", "@type": "WebSite", "@id": url + "#website",
                    "name": strip(s["name_plain"]) + " Manningtree", "url": url,
                    "inLanguage": "en-GB", "publisher": {"@id": url + "#business"}}]),
        chips="\n".join(f"          <span>{c}</span>" for c in s["chips"]),
        cards="\n".join(f'        <div class="item"><h3>{t}</h3><p>{d}</p></div>'
                        for t, d in s["cards"]),
        photos="\n".join(
            f'        <figure><img src="photos/{f}.jpg" loading="lazy" decoding="async"\n'
            f'          width="800" height="600" alt="{strip(c)} - {strip(s["name_plain"])}, Manningtree">'
            f'<figcaption>{c}</figcaption></figure>' for f, c in s["photos"]),
        perks="\n".join(f"          <span>{p}</span>" for p in s["perks"]),
        hours="\n".join(
            '        <div class="card"><h3>' + h + "</h3>"
            + "".join(f"<p>{l}</p>" for l in lines)
            + (f'<p class="small">{small}</p>' if small else "") + "</div>"
            for h, lines, small in s["hours"]),
        faqs="\n".join(f'        <div class="q"><h3>{q}</h3><p>{a}</p></div>' for q, a in s["faqs"]),
        socials="\n".join(f'      <a href="{u}" target="_blank" rel="me noopener">{n}</a>'
                          for n, u in s["socials"]),
        phone_line=phone_line,
        script=SCRIPT.substitute(hours_js=json.dumps(s["hours_js"])),
    ), encoding="utf-8")

    sections = []
    for heading, note, rows in s["sub_sections"]:
        body = "\n".join(
            '        <div class="r"><span class="n"><b>' + n + "</b>"
            + (f'<span class="d">{d}</span>' if d else "")
            + "</span>" + (f'<span class="p">{p}</span>' if p else "") + "</div>"
            for n, d, p in rows)
        sections.append(
            f'    <section>\n      <div class="head"><h2>{heading}</h2><div class="deco"></div></div>\n'
            + (f'      <p class="sub">{note}</p>\n' if note else "")
            + f'      <div class="rows">\n{body}\n      </div>\n    </section>\n')

    (out / s["sub_file"]).write_text(SUB.substitute(
        common,
        sub_jsonld=ld(sub_schema(s, url, sub_url)),
        flag=(f'    <p class="flag">{s["sub_flag"]}</p>\n' if s["sub_flag"] else ""),
        sections="\n".join(sections),
        phone_line=phone_line,
    ), encoding="utf-8")

    return len(s["cards"]), len(s["sub_sections"])



def build_guides(slug, s):
    """Stamp a copy of each guide with the business name on it.

    The guides are identical for every customer - the GitHub addresses are the
    same for everyone. The name is there purely so a link cannot be sent to the
    wrong shop by accident.
    """
    masters = {"domain": HERE / "guides" / "_domain.html",
               "changes": HERE / "guides" / "_changes.html"}
    out = HERE / "guides" / slug
    out.mkdir(parents=True, exist_ok=True)

    banner = (
      '<div class="who">Prepared for<br><b>{name}</b>'
      '<span>{addr}, Manningtree, {pc}</span></div>').format(
        name=strip(s["name_plain"]), addr=s["address"], pc=s["postcode"])
    css = ("""
  .who{ background:#1d1d20; color:#fff; border-radius:10px; padding:14px 18px;
    margin:0 0 26px; font-size:13px; letter-spacing:1px; text-transform:uppercase; }
  .who b{ display:block; font-family:Georgia,serif; font-size:22px; letter-spacing:0;
    text-transform:none; margin-top:3px; }
  .who span{ display:block; font-size:13px; letter-spacing:0; text-transform:none;
    color:#a8a8b0; margin-top:2px; }
""")
    for kind, src in masters.items():
        html = src.read_text(encoding="utf-8")
        html = html.replace("</style>", css + "</style>", 1)
        html = html.replace('<div class="wrap">\n', '<div class="wrap">\n' + banner + "\n", 1)
        (out / f"{kind}.html").write_text(html, encoding="utf-8")
    return out

if __name__ == "__main__":
    for slug, site in SITES.items():
        cards, secs = build(slug, site)
        build_guides(slug, site)
        print(f"  {slug:16} index.html + {site['sub_file']:14} ({cards} cards, {secs} sections) + 2 guides")
    print("\nDone. Same template, same sections, same order - only the data differs.")
