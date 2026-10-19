---
theme: default
title: ContentBridge
colorSchema: light
class: text-center
layout: center
---

# ContentBridge: link your systems, stay in sync

<!--
~20s. Hook. One team on one CMS, another on another, each with its own database.
How do you link the two and keep them in sync for efficient teamwork?
-->

---

# Problem

<div class="comm" v-show="$clicks < 3">
<div class="comm-row">
<div class="comm-person"><div class="comm-ic">🧑‍💻</div>Marketing team</div>
<div class="comm-mid">
<div v-click="1" class="comm-email">
<div class="tag">Email</div>
name: Aurora BX54 Fiber Laser Engraver<br>
description: The newly developed engraver BX54 ...<br>
related_product_ids: 104, 891, 233
</div>
<div v-click="1" class="comm-arrow">&#8592;</div>
</div>
<div class="comm-person"><div class="comm-ic">🧑‍🔧</div>Product team</div>
</div>
<div v-click="2" class="comm-note">Creates a new post, adds a custom field <code>related_product_ids</code></div>
</div>

<div v-show="$clicks >= 3" class="grid grid-cols-[1fr_2fr] items-start gap-6 mt-4">
<div class="min-w-0">
<div class="tag">WordPress · Post</div>
<div class="card">
<div class="card-title">Burn it with BX54</div>
<p>The newly developed engraver BX54 uses the most powerful laser there is to get its work done in a fraction of time. This saves not just unlimited time but has the advantage that the material need not be cooled to dissipate the extra energy imparted by the 50mW laser. <span :class="{ hl: $clicks >= 4 }">The BX54 is UL Listed and compliant with ANSI B11.1.</span></p>
<div class="meta"><code>related_product_ids</code> = <code>"104,891,233"</code></div>
</div>
</div>
<div class="min-w-0">
<div>
<div class="tag">Strapi · Product</div>
<table class="tbl">
<thead><tr><th>id</th><th>sku</th><th>name</th><th>legacyId</th><th>price</th></tr></thead>
<tbody>
<tr><td>1</td><td>SIS-BX54-ENGR</td><td>Aurora BX54 Fiber Laser Engraver</td><td>104</td><td>4299</td></tr>
<tr><td>2</td><td>SIS-BX54-FILTER</td><td>BX54 Fume Extraction Filter Cartridge</td><td>233</td><td>145</td></tr>
<tr><td>3</td><td>SIS-VER-SW100</td><td>Veridian GL100 Safety Interlock Switch</td><td>512</td><td>78</td></tr>
<tr><td>4</td><td>SIS-VER-ES200</td><td>Veridian ES200 Emergency Stop Pushbutton</td><td>618</td><td>54</td></tr>
<tr><td>5</td><td>SIS-VER-LC900</td><td>Veridian LC900 Type 4 Safety Light Curtain</td><td>734</td><td>612</td></tr>
<tr><td>6</td><td>SIS-BX54-LENS</td><td>BX54 Replacement Focus Lens</td><td>891</td><td>89</td></tr>
</tbody>
</table>
</div>
<div v-click="5" class="link-v"><span>N</span><hr><span>N</span></div>
<div v-click="5">
<div class="tag">Strapi · Certification</div>
<table class="tbl" style="width: 50%">
<thead><tr><th>name</th><th>ExpiryDate</th></tr></thead>
<tbody>
<tr><td>UL Listed</td><td>2026-12-31</td></tr>
<tr><td>CE Marked</td><td>2026-12-31</td></tr>
</tbody>
</table>
</div>
</div>
</div>

<div v-click="3" class="stack">
<div v-click="[3,6]" class="question">How do you link these?</div>
<div v-click="6" class="question">The tables in Strapi are linked, but nothing links the post to the certification. How do I resolve the post when it goes stale?</div>
</div>

<!--
Click 1: email from product to marketing: name, description, related_product_ids (104, 891, 233).
Click 2: marketing creates a new WordPress post, adds a custom field related_product_ids with that value.
Click 3: diagram clears, the real post + Strapi Product table appear. "How do you link these?" No shared key visible.
Click 4: highlight the sentence "UL Listed ... ANSI B11.1". Nothing links this claim to a certification.
Click 5: the Strapi Certification table appears. It IS linked to Product in Strapi (many-to-many), but not to the post.
Click 6: closing question.
NOTE: the seeded post doesn't contain the UL/ANSI sentence yet; add it to the live post so the demo matches.
-->

---

# Solution

<svg viewBox="0 0 920 420" class="sol">
<defs><marker id="ah-wp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#0f6e8c"/></marker><marker id="ah-st" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7a5ea8"/></marker><marker id="ah-x" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d9822b"/></marker></defs>
<text x="0" y="14" class="db" fill="#0f6e8c">WordPress</text><text x="480" y="14" class="db" fill="#5b4488">Strapi</text>
<rect x="0" y="30" width="120" height="90" rx="5" fill="#fff" stroke="#0f6e8c" stroke-width="2"/><path d="M0,54 V35 a5,5 0 0 1 5,-5 H115 a5,5 0 0 1 5,5 V54 Z" fill="#d9eef2" stroke="#0f6e8c" stroke-width="2"/><text x="60.0" y="47" text-anchor="middle" class="erd-h" fill="#0f6e8c">wp_postmeta</text><text x="8" y="70" class="erd-f">meta_id</text><text x="8" y="85" class="erd-f">post_id (FK)</text><text x="8" y="100" class="erd-f">meta_key</text><text x="8" y="115" class="erd-f">meta_value</text><rect x="160" y="30" width="120" height="90" rx="5" fill="#fff" stroke="#0f6e8c" stroke-width="2"/><path d="M160,54 V35 a5,5 0 0 1 5,-5 H275 a5,5 0 0 1 5,5 V54 Z" fill="#d9eef2" stroke="#0f6e8c" stroke-width="2"/><text x="220.0" y="47" text-anchor="middle" class="erd-h" fill="#0f6e8c">wp_posts</text><text x="168" y="70" class="erd-f">ID</text><text x="168" y="85" class="erd-f">post_title</text><text x="168" y="100" class="erd-f">post_content</text><text x="168" y="115" class="erd-f">post_status</text><rect x="320" y="30" width="120" height="75" rx="5" fill="#fff" stroke="#0f6e8c" stroke-width="2"/><path d="M320,54 V35 a5,5 0 0 1 5,-5 H435 a5,5 0 0 1 5,5 V54 Z" fill="#d9eef2" stroke="#0f6e8c" stroke-width="2"/><text x="380.0" y="47" text-anchor="middle" class="erd-h" fill="#0f6e8c">wp_terms</text><text x="328" y="70" class="erd-f">term_id</text><text x="328" y="85" class="erd-f">name</text><text x="328" y="100" class="erd-f">slug</text><line x1="120" y1="70" x2="160" y2="70" stroke="#0f6e8c" stroke-width="2"/><text x="123" y="64" class="card" fill="#0f6e8c">N</text><text x="157" y="64" text-anchor="end" class="card" fill="#0f6e8c">1</text><line x1="280" y1="70" x2="320" y2="70" stroke="#0f6e8c" stroke-width="2"/><text x="283" y="64" class="card" fill="#0f6e8c">N</text><text x="317" y="64" text-anchor="end" class="card" fill="#0f6e8c">N</text><rect x="480" y="30" width="120" height="75" rx="5" fill="#fff" stroke="#7a5ea8" stroke-width="2"/><path d="M480,54 V35 a5,5 0 0 1 5,-5 H595 a5,5 0 0 1 5,5 V54 Z" fill="#ece7f6" stroke="#7a5ea8" stroke-width="2"/><text x="540.0" y="47" text-anchor="middle" class="erd-h" fill="#5b4488">Certification</text><text x="488" y="70" class="erd-f">name</text><text x="488" y="85" class="erd-f">issuingBody</text><text x="488" y="100" class="erd-f">ExpiryDate</text><rect x="640" y="30" width="120" height="105" rx="5" fill="#fff" stroke="#7a5ea8" stroke-width="2"/><path d="M640,54 V35 a5,5 0 0 1 5,-5 H755 a5,5 0 0 1 5,5 V54 Z" fill="#ece7f6" stroke="#7a5ea8" stroke-width="2"/><text x="700.0" y="47" text-anchor="middle" class="erd-h" fill="#5b4488">Product</text><text x="648" y="70" class="erd-f">id</text><text x="648" y="85" class="erd-f">legacyId</text><text x="648" y="100" class="erd-f">name</text><text x="648" y="115" class="erd-f">sku</text><text x="648" y="130" class="erd-f">price</text><rect x="800" y="30" width="120" height="60" rx="5" fill="#fff" stroke="#7a5ea8" stroke-width="2"/><path d="M800,54 V35 a5,5 0 0 1 5,-5 H915 a5,5 0 0 1 5,5 V54 Z" fill="#ece7f6" stroke="#7a5ea8" stroke-width="2"/><text x="860.0" y="47" text-anchor="middle" class="erd-h" fill="#5b4488">Standard</text><text x="808" y="70" class="erd-f">name</text><text x="808" y="85" class="erd-f">organization</text><line x1="600" y1="70" x2="640" y2="70" stroke="#7a5ea8" stroke-width="2"/><text x="603" y="64" class="card" fill="#5b4488">N</text><text x="637" y="64" text-anchor="end" class="card" fill="#5b4488">N</text><line x1="760" y1="70" x2="800" y2="70" stroke="#7a5ea8" stroke-width="2"/><text x="763" y="64" class="card" fill="#5b4488">N</text><text x="797" y="64" text-anchor="end" class="card" fill="#5b4488">N</text>
<g v-click="1"><text x="460" y="176" text-anchor="middle" class="tr">tables → nodes · relations → predicate edges</text><text x="460" y="196" text-anchor="middle" class="tr-a">↓</text><rect x="170.0" y="212.0" width="100" height="36" rx="18.0" fill="#d9eef2" stroke="#0f6e8c" stroke-width="2"/><text x="220" y="235" text-anchor="middle" class="n-t" fill="#0f6e8c">Post</text><rect x="10" y="285" width="150" height="46" rx="12" fill="#d9eef2" stroke="#0f6e8c" stroke-width="2"/><text x="85" y="305" text-anchor="middle" class="n-t" fill="#0f6e8c">PostMeta</text><text x="85" y="321" text-anchor="middle" class="n-s">related_product_ids</text><rect x="320.0" y="290.0" width="100" height="36" rx="18.0" fill="#d9eef2" stroke="#0f6e8c" stroke-width="2"/><text x="370" y="313" text-anchor="middle" class="n-t" fill="#0f6e8c">Term</text><line x1="190" y1="246" x2="120" y2="284" stroke="#0f6e8c" stroke-width="2" marker-end="url(#ah-wp)"/><text x="130" y="262" text-anchor="end" class="p-l" fill="#0f6e8c">hasMeta</text><line x1="250" y1="246" x2="335" y2="284" stroke="#0f6e8c" stroke-width="2" marker-end="url(#ah-wp)"/><text x="310" y="262" text-anchor="start" class="p-l" fill="#0f6e8c">hasTerm</text><rect x="650.0" y="212.0" width="100" height="36" rx="18.0" fill="#ece7f6" stroke="#7a5ea8" stroke-width="2"/><text x="700" y="235" text-anchor="middle" class="n-t" fill="#5b4488">Product</text><rect x="495.0" y="290.0" width="110" height="36" rx="18.0" fill="#ece7f6" stroke="#7a5ea8" stroke-width="2"/><text x="550" y="313" text-anchor="middle" class="n-t" fill="#5b4488">Certification</text><rect x="800.0" y="290.0" width="100" height="36" rx="18.0" fill="#ece7f6" stroke="#7a5ea8" stroke-width="2"/><text x="850" y="313" text-anchor="middle" class="n-t" fill="#5b4488">Standard</text><line x1="670" y1="246" x2="585" y2="284" stroke="#7a5ea8" stroke-width="2" marker-end="url(#ah-st)"/><text x="570" y="262" text-anchor="end" class="p-l" fill="#5b4488">hasCertification</text><line x1="730" y1="246" x2="815" y2="284" stroke="#7a5ea8" stroke-width="2" marker-end="url(#ah-st)"/><text x="790" y="262" text-anchor="start" class="p-l" fill="#5b4488">conformsTo</text><line x1="460" y1="150" x2="460" y2="330" stroke="#d6dde3" stroke-dasharray="4 4"/></g>
<g v-click="2"><path d="M85,331 C85,412 700,412 700,250" fill="none" stroke="#d9822b" stroke-width="3" marker-end="url(#ah-x)"/><rect x="305" y="383" width="310" height="24" rx="4" fill="#fff"/><text x="460" y="400" text-anchor="middle" class="x-l" fill="#d9822b">skos:closeMatch  ·  related_product_ids = legacyId</text></g>
</svg>

<!--
Start: both databases as ERDs. WordPress: posts, post meta (where related_product_ids lives), terms.
Strapi: product, certification, standard (many-to-many).
Repose the question: how do you link them? Answer: transform the databases into graphs.
Click 1: tables become nodes, relations become edges with predicates. Just a sketch, real graphs are bigger.
Say: just like tables inside a database are linked by predicates, we can link nodes across databases.
Click 2: the cross-database edge: related_product_ids = legacyId (skos:closeMatch, same predicate as in mapping-ontology.ttl).
Predicates hasMeta/hasTerm/hasCertification/conformsTo are illustrative only.
-->

---

# Value Proposition

<div class="vp">
<div class="vp-head"><div></div><div>Today</div><div>With ContentBridge</div></div>
<div v-click="1" class="vp-row">
<div class="vp-topic">Linking content across systems</div>
<div class="vp-today">Someone digs through both schemas and writes a one-off script that breaks when a schema changes.</div>
<div class="vp-now">The link is discovered and recorded as a reusable mapping. Nothing is migrated.<span class="vp-chip">Easier · reusable</span></div>
</div>
<div v-click="2" class="vp-row">
<div class="vp-topic">Resolving stale posts</div>
<div class="vp-today">A certification expires and someone has to remember, or search, for every post that cites it.</div>
<div class="vp-now">The lapse is detected, and the affected posts are found and updated. A human approves.<span class="vp-chip">Faster · nothing slips through</span></div>
</div>
</div>

<div v-click="3" class="question">No expired certification stays live on the website, and no system has to be migrated.</div>

<!--
Compare how it is solved today vs. with ContentBridge, on the two issues from the problem slide.
Click 1: linking. Today: manual reverse-engineering, a one-off script per pair of systems. Now: the mapping is discovered and kept.
Click 2: stale posts. Today: depends on someone remembering. Now: the lapse triggers the search and the update.
Click 3: the benefit for the customer.
No numbers on purpose. Only add one if you can back it up, e.g. measure in the live demo how long it takes to find all
affected posts with ContentBridge vs. by hand, and say exactly that.
-->

---
layout: statement
---

# "DEMO."

<!-- ~30s. The proof point. Say what happened: the Strapi date lapsed, the posts that cite it were found and updated. -->

---

# Team

**Vishnudev, solo founder**

- **LLM agents:** multi-agent orchestration, structured output, human-in-the-loop
- **Semantic data:** ontologies, RDF, SSSOM mappings
- **Full-stack:** Python/FastAPI, React, WordPress and Strapi integration

<!-- ~30s. Every skill maps to a piece of the product you can point at in the repo. -->

---
layout: center
---

# Pilot it on your messy data

Built and tested on a demo stack, never on a real company's databases. That's the gap, and the ask:

**One team with two content systems and a date that matters.**

Open source, MIT-licensed: github.com/**vishnudevramachandra/Content-Bridge**

<!--
~30s. The honest gap and the call to action in one beat:
you haven't run this on real company data, so you want a pilot partner to do it with.
-->
