# Váš Lekár — Brainstorm brief: Prečo nepredávame premium balíčky a čo s tým

**Téma:** Výsledky kampaní rastú, ale predáva sa nízko-ticket (1× vstupy), nie ročné členstvá a preventívne prehliadky. Klientovi to vadí — a má pravdu: bez high-ticket mixu sa PNO cieľ < 8 % matematicky nedá dosiahnuť.
**Pripravil:** CreAI / Matej · 12. jún 2026 · Podklady: W23 report (8.6.), handoff, marcová G Ads analýza, web klienta (cenník overený 12.6.)

---

## 1. Problém v kocke

| Metrika W23 (1.–7.6.) | Hodnota | Kontext |
|---|---|---|
| Objednávky | 55 (+22 % WoW) | Akvizícia funguje |
| Revenue (net, CRM) | €6,175 (-4.1 %) | Rastieme v kusoch, nie v eurách |
| AOV | €112 (-21.5 %) | Mix sa zosypal na nízko-ticket |
| Performance PNO | 18.78 % | Cieľ < 8 % — sme 2.3× nad ním |

**Produktový mix W23:** 42 objednávok = jednorazové vstupy (€3,128; 51 % revenue). High-ticket len 4 objednávky — 2× členstvo PREMIUM (€1,198) + 2× prehliadka MAX (€1,258) = 40 % revenue. Minulé týždne mali pestrejší mix (PLATINUM, SMART, COMFORT) — high-ticket predaje sú zatiaľ **náhodné, nie systémové**.

**Kľúčová rovnica:** Pri spende €1,228/týždeň potrebujeme na PNO 8 % revenue ~€15,350/týždeň — 2.5× viac než dnes. Objemom 1× vstupov (€59) sa tam nedostaneme nikdy: to by bolo +155 vstupov/týždeň navyše. Cez členstvá by stačilo ~15 členstiev/týždeň navyše — stále veľa, ale o rád realistickejšie v kombinácii s úpravou cieľa.

---

## 2. Ekonomika produktov očami zákazníka (z webu, overené 12.6.)

| Produkt | Cena | Poznámka |
|---|---|---|
| 1× / 2× / 3× vstup | €59 / €109 / €159 | Multi-vstupy už zľavnené (€53–54.5/vstup) |
| Členstvo COMFORT | €449 | 10 vstupov, 10 % zľavy, 1× USG/RTG |
| Členstvo PREMIUM | €599 | Neobmedzené vstupy, 15 % zľavy, 3× USG/RTG |
| Členstvo PLATINUM | €990 | Neobmedzené, 20 % zľavy, 5× USG/RTG |
| Prehliadka BASIC / SMART / MAX | €349 / €449 / €629 | + DNA analýza €299 |
| Ročná karta VL / Gyneko | €99 / €119 | Kapitácia |

**Prečo racionálny zákazník členstvo nekúpi:** COMFORT (€449) sa oplatí až od ~8 návštev/rok. Bežný človek rieši 1–2 akútne problémy ročne — a my mu sami predávame zľavnené 2×/3× balíčky, ktoré členstvo ďalej kanibalizujú. Skok €59 → €449 je 7.6×, bez medzistupňa, bez mesačných platieb, bez trialu. **Členstvo dáva zmysel len prevencii/longevity zákazníkovi alebo chronikovi — a na toho dnes nemierime.**

**Nevyužitá hodnota:** web tvrdí, že členovia majú Rozšírenú preventívnu prehliadku v cene (SMART = €449 hodnota pri PREMIUM €599). Ak to platí, PREMIUM je „prehliadka + neobmedzený rok k tomu za €150" — tento framing v kampaniach nikde nie je. *(Overiť presné podmienky s klientom.)*

---

## 3. Hypotézy, prečo premium nepredávame

**H1 — Štrukturálny mismatch funelu (najsilnejšia).** Celý Google Ads účet je postavený per-špecializácia (SRCH Urológia, ORL…). Ten zachytáva **akútny, symptómový dopyt** — človek s boľavým uchom chce termín teraz, kúpi 1× vstup a odíde. Členstvo je **preventívna, high-consideration kúpa** — iný človek, iný moment, iný funnel. Akvizičný stroj teda systémovo vyrába nízko-ticket; nie je to chyba optimalizácie, ale dizajnu.
*Overenie:* search terms report — aký podiel queries je symptómových vs. preventívnych.

**H2 — Chýba upsell po návšteve.** Týždenne prejde klinikou ~55 platiacich zákazníkov s čerstvou dobrou skúsenosťou — najlepší moment na predaj členstva. Dnes neexistuje mechanizmus: recepcia nepredáva, follow-up e-mail nejde, kúpený vstup sa pri upgrade neodpočíta. Toto je proces klienta, nie médiá — ale má najvyššiu páku.
*Overenie:* spýtať sa klienta, čo sa deje po návšteve; koľko členov boli predtým jednorazoví zákazníci (CRM).

**H3 — Cesta k členstvu na webe/checkoute nepodporuje rozhodnutie.** Pri kúpe 2×/3× vstupu sa nikde nezobrazí porovnanie s COMFORT. Homepage má expirované promá („platí do 31.08.2025" — visí tam 10 mesiacov), endo/imuno/kardio vyžadujú min. 2 vstupy (€109 bariéra vs. komunikovaných „od 59 €"). High-consideration produkt nemá nurture: žiadny remarketing na návštevníkov členskej stránky, žiadna e-mail sekvencia, žiadna možnosť konzultačného callu.
*Overenie:* UX prechod checkoutu + MS Clarity na členskej LP.

**H4 — Možno predávame viac, než vidíme (atribúcia).** Pixel zachytí 3 z 55 objednávok (5 %). Členstvá konvertujú cez dlhé, multi-session cesty — presne tie, ktoré slepá atribúcia stráca. Peter v W23 zdvihol spend na členstvo +183 % a CRM ukázal 2× PREMIUM — súvis nevieme dokázať ani vyvrátiť. **Riziko: vypneme niečo, čo funguje.** GA4 + pixel + offline conversion import z CRM je predpoklad všetkého ostatného.

**H5 — Kapacitný strop ohrozuje promise.** Členstvo predáva „rýchle termíny bez čakania", ale Imunoalergológia je na 79 %, Kardio 76 % vyťaženosti (apríl — novšie dáta nemáme). Ak by členstvá rástli, promise sa zlomí presne tam, kde je dopyt. Bez aktuálneho exportu vyťaženosti nevieme, čo si môžeme dovoliť škálovať.

---

## 4. Smery riešení (na diskusiu)

### A. Médiá — rozdeliť funnel na dva stroje
- Akútny dopyt (per-špecializácia SRCH) nechať na 1× vstupy — funguje, nesiliť doň členstvá.
- Postaviť samostatný **prevenčný/longevity funnel** na členstvá a prehliadky: Meta + obsah (Boris Bajer, „klient ≠ pacient", dáta a dlhovekosť — positioning už existuje, len sa nepoužíva v performance), remarketing na 1.4k link-klikov/týždeň a na návštevníkov členskej LP.
- Prehliadky (€349–629) ako **vstupný high-ticket produkt** — jednorazové rozhodnutie, ľahšie než ročný záväzok; člen z prehliadky je prirodzený ďalší krok.

### B. Produkt / pricing — návrhy pre klienta (bez neho sa mix nepohne)
- **Mesačné platby** (€45–55/mes.) — zlomí bariéru €449 naraz.
- **Kredit za vstup**: kúpený 1×/2× vstup sa do 30 dní odpočíta z členstva → upgrade je no-brainer.
- Zvážiť, či 2×/3× zľavnené balíčky nekanibalizujú členstvo (možno nahradiť kreditom).
- Framing PREMIUM cez zahrnutú prehliadku SMART („prehliadka €449 + celý rok neobmedzene za €150 navyše").

### C. Proces klienta — upsell loop
- Skript pre recepciu + ponuka pri odchode; follow-up e-mail 24–48 h po návšteve s kreditom.
- E-mailová sekvencia na databázu jednorazových zákazníkov (najteplejšie publikum, nulový media cost → zlepšuje PNO okamžite).

### D. B2B kanál — obísť PNO úplne
- Business Comfort/Premium/Platinum už existujú; klinika berie Edenred, Up Déjeuner, Benefit Plus. Predaj cez HR firiem (Eurovea, BA biznis komunita) = high-ticket objem bez ad spendu. Otázka: kto to predáva — klient, my, nikto?

### E. Tracking — predpoklad, nie option
- GA4 e-commerce + Meta pixel dokončiť, CRM offline import (enhanced conversions / CAPI). Bez toho nevieme vyhodnotiť žiadny z experimentov vyššie.

---

## 5. PNO realita — pripraviť rozhovor s klientom

- Blended PNO < 8 % pri AOV €112 a súčasnom spende je nedosiahnuteľné — treba to povedať nahlas a preformulovať cieľ.
- Návrh: **PNO per produktová línia** — akútne vstupy (nízke PNO, brand + PMax), členstvá/prehliadky (vyššie akceptovateľné CAC vďaka LTV: člen = €449–990 + renewal + zľavnené úkony počas roka).
- Meta cost/purchase €316 je katastrofa pre €59 vstup, ale prijateľný CAC pre €599 členstvo — bez fixu atribúcie však reálny CAC členstva nepoznáme.
- Otázka na klienta: aké sú marže per línia a hodnota renewalu? Bez toho je 8 % číslo bez podkladu.

---

## 6. Návrh agendy brainstormu (60–90 min)

1. **Čísla a problém** (10 min) — sekcie 1–2 tohto briefu.
2. **Hypotézy H1–H5** (20 min) — ktorým veríme, čo vieme overiť do týždňa.
3. **Smery A–E** (30 min) — vybrať 2–3 experimenty na najbližšie 2–4 týždne; každý s metrikou úspechu a ownerom.
4. **PNO rozhovor s klientom** (15 min) — kto, kedy, s akým návrhom redefinície cieľa.
5. **Next steps** (5 min).

**Navrhované prvé experimenty (quick wins):** (1) e-mail upsell sekvencia na CRM databázu — nulový spend, meriame predané členstvá; (2) remarketing audience z členskej LP + nový framing PREMIUM cez zahrnutú prehliadku; (3) tracking fix ako paralelný workstream; (4) vyžiadať od klienta aktuálnu vyťaženosť + marže per línia pred škálovaním.

---

## 7. Otvorené otázky na tím

- Vieme z CRM histórie, koľko % členov začalo jednorazovým vstupom? (definuje silu H2)
- Prečo W22 predal PLATINUM+SMART+MAX+COMFORT a W23 takmer nič — bola za tým nejaká aktivita (post, kampaň, odporúčanie lekára), alebo šum?
- Kto vlastní vzťah s klientom na produktové zmeny (mesačné platby, kredit za vstup) — Jozef Z.?
- Chceme B2B predaj poňať ako našu službu (outreach, materiály), alebo len odporučiť klientovi?
- Meta refresh kreatív (ad fatigue signály z W23) — spojiť rovno s novým členským messagingom?

---

*Zdroje: W23 weekly report (SOLUTIONS/accounts/weekly-report-vaslekar/, extrakcia 8.6.), vaslekar-brainstorm-handoff.md, vaslekar-google-ads-analyza-marec-2026.md, poliklinika.vaslekar.sk (12.6.2026). Čísla revenue/objednávky = CRM od klienta; Meta/G Ads = Supermetrics. Atribučné čísla (3 omni purchases) brať ako podhodnotené.*
