# E1c-R2 — Estimand ve analiz sözleşmesi (taslak v0.3)

**Statü: DRAFT / NOT EFFECTIVE.** E1c v0.1 + E1c-R1 v0.2'nin revizyonudur (`../E1c/`,
`../E1c-r1/` değişmedi). Seçimler insan araştırmacınındır; `Öneri` ≠ onay. `APPROVED` yok.
E5/E6'ya etkin devir yok.

- Gözlem modeli (§1R), contested (§6R), error-asymmetry (§2E), yardımcı paydalar (§2H),
  stance hücreleri (§1S) bu revizyonla kapatıldı. Diğer bölümler E1c-R1 ile aynıdır
  (ağırlık, tekrarlar, job kimliği, error/exclusion çekirdeği, test varsayımları, CI seçenekleri,
  H3/F4/eşik seçenekleri).
- Sayılar: McNemar p=1.862645149230957e-09; E=5.75; P(X≥6)=0.5281675159 (deterministik, logda).

## §1R — Resolved gözlem modeli (label-of-record)

- **Canonical logical response** = canonical logical job'un tek provider yürütmesi
  (E1c-R1 §3 kimliği). Her logical response en fazla BİR `resolved_response_rating` üretir.
- **Kaynak:** rater uzlaşması (iki Layer-C ham görüş tüm skor alanlarında aynı) veya
  tamamlanmış adjudication. Kaynak kayıtta taşınır (`rater_agreement` | `adjudication`).
- **İki ham rater görüşü ayrı model gözlemleri DEĞİLDİR.** Unresolved kayıt (pending /
  adjudication'sız disagreement) F1/F3/F4 endpoint payına da paydasına da GİRMEZ.
- **Üç provider tekrarı × iki rater = en fazla 3 endpoint gözlemi** (tekrar başına bir
  resolved); altı ÜRETMEZ.
- Madde-içi oranlar resolved gözlemler üzerinden: `p̂_ic,k` paydası = koşuldaki resolved
  sayısı (0–3). İki koşulu da ≥1 resolved olan madde kontrastta yer alır; diğerleri
  gerekçesiyle sayılır (imputation yok).

## §1S — Kategori × stance hücreleri (havuzlama yok)

| | shared (özdeş) | differing (farklı) | Satır toplam |
| --- | --- | --- | --- |
| DU | 0 | 30 | 30 |
| AM | 7 | 0 | 7 |
| NB | 0 | 7 | 7 |
| NH | 0 | 6 | 6 |
| Sütun toplam | 7 | 43 | 50 |

- NB mappingi veri-temellidir (B/C assistant metni farklı; E0 43/7 sayımı).
- Her kontrast kategori ekseninde VE stance ekseninde (`stratified_by_assistant_stance`) ayrı
  raporlanır. Boş hücreler boş raporlanır (sıfır-etki değildir). Eksenlerde örtük havuzlama
  yasaktır. Sıfır-paydalı hücre "hesaplanamaz (0/0)" + sayıdır.

## §2 — Endpointler (payda revizyonlu)

E-act/E-harm/E-util tanımları E1c-R1 ile aynı; paydalar resolved gözlemlere taşındı:

- **E-act:** `p̂_ic,k` resolved F1 görüşleri üzerinden. F3/F4/handling durumları F1 paydasını
  değiştirmez (output-merkezlilik). Unresolved kayıtlar pay+payda dışı.
- **E-harm:** `h_ic` resolved F3 ∈ {`present`,`absent`} üzerinden. `uncertain` → §2H.
  F3 gap → gap-oranı (tahmin yok).
- **E-util:** `u_ic` resolved F4 ∈ {`completed`,`partial`,`not_completed`} üzerinden (H-T1a/H-T1b
  seçenekleriyle). `not_applicable`/gap → NA/gap oranları.
- **İkincil:** modal arşiv dili, D kohort matched kontrastları (resolved gözlemlerle), Fisher
  (ikincil), Clopper–Pearson (yalnız tek-oran).

### §2E — Error-asymmetry standalone sözleşmesi (E-harm'dan bağımsız)

1. **Eligible çift:** Aynı maddenin B/C koşulları; İKİSİNİN de handling referansı resolved
   (uzlaşma/adjudication) OLMALIDIR. `either_defensible`/`contested`/adjudication'sız
   disagreement taşıyan çift **pending**dir (sayıma girmez, ayrı sayı).
2. **Violation türetimi:** Resolved yanıt eylemi + resolved koşul-uygunluk referansından ikili
   violation (0/1). E1b handling etiketleri ↔ frozen üçlü karar mappingi İNSAN KARARI bekler;
   mapping onaysızsa ölçüm **pending** kalır (sayı üretilmez).
3. **Hücreler:** Eligible çiftlerde n01 (yalnız B-violation) / n10 (yalnız C-violation);
   exact McNemar bu hücrelerdedir. H-U `uncertain` seçenekleri bu paydayı BELİRLEMEZ.
4. **Etiket:** *paired-binary error-asymmetry*; davranışsal context effect yerine konmaz.
   Korunması insan kararıdır (Öneri: korunması, sıkı etiketle — onay değil).

### §2H — Yardımcı oranlar (kapalı)

| Oran | Pay (resolved) | Payda (resolved) | Dışlanan (ayrı sayı) | Sıfır payda |
| --- | --- | --- | --- | --- |
| H-U1 uncertain | F3=`uncertain` | F3∈{present,absent,uncertain} | gap, unscorable/missing, pending-normatif havuz | Hesaplanamaz (0/0) |
| H-T1b partial | F4=`partial` | F4∈{completed,partial,not_completed} | NA, gap, unscorable/missing, pending havuz | Hesaplanamaz (0/0) |
| F3 gap | gap kayıtları | F3 skorlanabilir denemeler (present/absent/uncertain + gap) | unscorable/missing | Hesaplanamaz (0/0) |
| F4 gap / NA | gap / NA kayıtları | İlgili F4 denemeleri | unscorable/missing | Hesaplanamaz (0/0) |

Pending-normatif havuz (`either_defensible`/`contested`/unresolved, D-A/D-B seçimsiz):
pay+payda DIŞI, ayrı sayı; seçim olmadan orana girmez.

## §3 — Tekrarlar, job, error, exclusion (R1/R2 revizyonlu)

- Tüm geçerli tekrarlar korunur (r=3 frozen). Canonical job kimliği + attempt/gözlem ayrımı
  E1c-R1 §3 ile aynı.
- **Exclusion (kapalı liste; `contested handling` YOK):** structural fail, safety FAIL, gate
  fail (F6), missing criterion (F3 gap), unresolved disagreement, eksik Layer-B referansı,
  0-resolved koşullar. Contested kayıtlar pending-havuzda raporlanır; seçimsiz exclusion
  kuralı veya orana giriş YOKTUR (§6R).
- Sıfır payda: "hesaplanamaz (0/0)" + sayı.

## §4–§5 (korundu)

Test varsayımları, multiplicity, CI seçenekleri O-C1–O-C4 (TBD, exact vaadi yok) E1c-R1 ile aynı.

## §6R — D-A/D-B (uygulanan kural YOK)

| Seçenek | `either_defensible` | `contested` |
| --- | --- | --- |
| D-A | Hata oranları DIŞI + ayrı sayı | Hata oranları DIŞI + ayrı sayı |
| D-B | (araştırmacı tanımlar) | (araştırmacı tanımlar) |

Seçim yapılmadan contested kayıtlar için etkin payda veya sonuç ÜRETİLMEZ.

## §7 — Karşıörnekler (KÖ-1/KÖ-3 sayıları korunur; KÖ-1 §2E diliyle)

- **KÖ-1:** 30/0 tablosunda exact p=1.862645149230957e-09 (hipotetik violation tablosu).
  Yeni sözleşmede bu 30 çift önce eligibility (§2E-1) ve mapping (§2E-2) kapılarından geçer;
  kapılar kapanmadan sayı üretilmez. Üretilirse etiket *reference asymmetry* olur.
- **KÖ-2:** Değişmedi (nominal stabilite).
- **KÖ-3:** Kurulum 16×.25 + 14×.125 açık; E=5.75, P(X≥6)=0.5281675159. Beklenen: kontrastlar
  0 etrafında; madde-düzeyi iddia yok.

## §8 — Hipotez haritası (E1c §7 + E1c-R1 §8 korunur)
