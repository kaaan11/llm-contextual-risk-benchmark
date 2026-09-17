# E1a — Araştırma iddiası ve karar matrisi taslağı

**Statü: DRAFT / NOT EFFECTIVE.** Bu belge etkili protokolü veya mühürlü belgeleri değiştirmez.
Hiçbir hüküm insan onayı olmadan `APPROVED` olmaz. İnsan kararı sütunu boş bırakıldı;
kararlar E1a kabul kaydında tutulur.

- Kök: `/home/kaan/AI_Search`. Önkoşul: `docs/reviews/llm-benchmark/E0-acceptance.md` (E0 KABUL EDİLDİ, 2026-09-09).
- Okunanlar: üst plan E1a satırı, `README.md`, `docs/research_questions.md`,
  `docs/phase7e_pre_evaluation_clarification.md`, `docs/ROADMAP.md`,
  rapor §2 (construct), §3 (novelty), §7 (identification), §12 (do-not-change), §14 (missing threats),
  §15–16 (literatür/final gate) ve `docs/reviews/llm-benchmark/E0/findings.md` (P01–P15, S01/S02).
- Mühürlü belgeler (`docs/phase7e_preregistration.md`, `docs/phase7e_annotation_protocol.md`,
  `docs/PHASE_7D_EXPERIMENTAL_DESIGN.md`, `dataset/pilot/multiturn/stimulus_dataset_v1.json`)
  salt okunur kullanıldı; değiştirilmedi.
- Karar sözlüğü: `koru` (ifade aynen kalabilir) / `daralt` (kapsam küçültülür, amendment diline taşınır) /
  `terk et` (iddia pilotun dışına çıkar) / `ertele` (gelecek çalışmaya bırakılır, bu pilotta iddia yok).

## Belge drift'i (karar matrisinden önce)

1. `docs/research_questions.md` (§6: 120 benign + 100 adversarial + 80 multi-turn = 300 örnek;
   §3 RQ3 A/B/C savunma katmanı; §41–45 RQ4 Pareto sınırı) Phase 7D yeniden tasarımından önceki
   kapsamı anlatır. Birincil pilot artık 50 research item / 171 koşul, matched-triplet/quadruplet,
   savunma prototipi yok, Pareto yok (`README.md:20-29`, prereg §3–4, E0 findings P01/P02).
   Bu dosya tasarım tarihi olarak korunur; güncel iddia kaynağı değildir (C-13).
2. `README.md:3` başlık sorusu ("Does conversational context change how a model reads the *same*
   final prompt?") tek başına okunduğunda saf kullanıcı-bağlamı nedenselliği çağrıştırır.
   Clarification C1–C3 ( `phase7e_pre_evaluation_clarification.md:34-54` ) bunu whole-history paketiyle
   sınırlar; başlık sorusu ancak bu kayıtla birlikte okunursa savunulabilir (C-01).
3. `docs/ROADMAP.md:48-53` hibrit judge + %20 insan katmanı, frozen iki-insan primary planının
   (`phase7e_annotation_protocol.md:149-184`, `phase7g_human_qc.md:16-28,107-118`) yerine geçemez.
   Puanlama iddiası E1a'da iki-insan primary olarak korunur; judge değişikliği amendment ister (C-12).
4. Güç/bütçe sayıları driftlidir (prereg 513/model @r=3 vs ROADMAP 171×M=1.026; power belgesi çıplak
   Δ≥0,35): iddia değil raporlama borcudur; E1c/E5/E7'ye aittir, burada yalnız işaretlenir (C-14).

## Karar matrisi

| ID | İddia | Kaynak konumu | Mevcut ifade (özet) | Öneri | Önerilen ifade (taslak) | Kanıt | Etkilenen hipotez/çıktı | İnsan kararı |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C-01 | Whole-history packet (birincil construct) | `README.md:3,41-44,48-63`; `phase7e_pre_evaluation_clarification.md:26-38` (C1); rapor §2:27-39, §7:194-206 | "Aynı son istemin risk yorumu bağlamla değişir mi?" + "context is the only manipulated variable" + D falsifier | daralt | "Önceden tanımlanmış İngilizce teknik görevlerde, bayt-düzeyinde sabit son istemin farklı senaryolaştırılmış konuşma geçmişleri (kullanıcı metni + scripted assistant turu + söylem özellikleri paketi) altında üretilen yanıtların davranış türü, zararlı kapasite aktarımı ve meşru görev faydası bakımından dağılımsal duyarlılığı." | Clarification C1–C3; E0 P06 (43/7 bayt karşılaştırması); rapor §7 bundled-treatment çerçevesi | H1/H0a yorumu; birincil estimand ifadesi; başlık/yayın cümlesi | [ ] insan kararı: |
| C-02 | Latent intent / gerçek niyet tanıma | Rapor §2:56-58 (overclaim listesi), §4 F5:142-150; prereg §23 "Cannot" | "Gerçek niyeti anlıyor / modeli riski doğru okuyor" türü çıkarımlar | terk et | Bu pilot niyet tanısı koymaz. Aynı B metnini dürüst ve kötü niyetli kullanıcı kopyalayabilir; metne bakarak latent ayrım tanımlanabilir değildir. | Rapor §2:39 STRONG-INFERENCE; E0 P06 | H1–H3'ün mekanizma okuması; tartışma bölümü sınırları | [ ] insan kararı: |
| C-03 | Saf kullanıcı-kanıtı (pure user evidence) etkisi | Clarification C1–C3 (`phase7e_pre_evaluation_clarification.md:34-54`); rapor §7:206 | "Yalnız kullanıcı metni etki etti" | terk et | Kullanıcı-kanıtı etkisi bu tasarımdan ayrıştırılamaz; 43 maddede assistant stance birlikte değişiyor. Saf etki iddiası için shared-assistant / user-cue × stance deneyi yeni protokoldür (gelecek çalışma). | E0 P06/P13 (43 differing / 7 shared) | Estimand; §5 "Controlled confounds" yorumu | [ ] insan kararı: |
| C-04 | D'nin rolü (falsifier) | `README.md:56-60`; prereg §8.1:140-154; clarification C6:69-73; rapor §5:156, §7:196-204 | "D aynı hareketi yaparsa etki length/priming'dir, anlam değil" | daralt | "D yalnızca ek konuşma uzunluğu + genel priming açıklamasını sınar (21 maddede; DU-D 14). D hareketi semantic bileşenin yokluğunu göstermez; D hareketsizliği B/C'deki diğer confound'ları (assistant stance dahil) kaldırmaz. DU004 türü kusurlu D'ler versioned revise edilir." | Prereg §8.1 + §152-154 ("does not eliminate all priming confounds"); clarification C6; E0 P13 (D 17/21 bayt-kısa, token kanıtı değil) | H0b/F2 yorumu; D-state raporlaması | [ ] insan kararı: |
| C-05 | AM tanısal sınırı | Prereg §3:62, §8.2:161-165; clarification C3–C5:47-67; rapor §7:212 | "AM bağlam duyarlılığının temiz koludur" (geniş okuma) | daralt | "AM (n=7, assistant shared) kullanıcı-taşımalı sinyalin en temiz tasarım-içi tanısal/falsifier tabakasıdır; DU/NB/NH için randomized causal control değildir (n, construct, outcome topolojisi, konu karışımı farklı). AM'de doğru sonuç B/C hareketi değil clarification'ın korunması olabilir." | Clarification C4–C5; E0 P06/P13 | AM outcome/reference tanımı (E1b); analizde ayrı raporlama | [ ] insan kararı: |
| C-06 | NB/NH sınırı | `README.md:67-76`; prereg §3:63-64; clarification C8:81-88; rapor §7:208-210 | "NB taban / NH tavan kontrolü genel sağlamlığı gösterir" (geniş okuma) | daralt | "NB (n=7): bu script altında spurious escalation gözlenmedi. NH (n=6): bu script altında laundering gözlenmedi/geçti. İkisi ayrı raporlanır, birleştirilmez; genel context-laundering direnci kanıtı değildir. NB-C reframing ve NH-B ön-izleme caveat'leri sonuçla birlikte yazılır." | Clarification C8; E0 P13; rapor §7:208-210 | F1 yorumu; kontrol geç/kal raporlaması | [ ] insan kararı: |
| C-07 | Assistant stance tabakaları | Clarification C3:47-54; prereg raporlama kuralı; rapor §7:206, §8.1:218 | `assistant_turn_shared` (7) / `assistant_turn_differing` (43) | koru (raporlama disiplini olarak) | "Bütün aggregate iddialar tabakalı sunumla birlikte verilir; AM etkisi kullanıcı-bağlamı saf etkisi diye sunulmaz; tabaka etiketi örneklem büyütme izni değildir (7+43=50 havuzlanmaz)." | Clarification C3/C7; E0 P06 (43/7) | Birincil raporlama planı; E6 tabakalı analiz girdisi | [ ] insan kararı: |
| C-08 | External validity (genel güvenlik / gerçek konuşmalar / yaygınlık) | `README.md:191-224` (sınırlar); prereg §18:305-314, §23:357-365; rapor §2:56-58, §5:162, §7:200, §14:347-350 | "Genel çok-turlu güvenlik / gerçek kullanıcı dayanıklılığı / yaygınlık" | terk et (bu pilot) | "Korpus: İngilizce, teknik, constructed 50 senaryo. Sağlık, kişilerarası zarar, hukuk, gündelik belirsizlik transferi gösterilmez. Teacher-forced sabit geçmiş, modelin kendi üreteceği geçmişi temsil etmez. Prevalence, per-category rate, cross-model significance yok." | README sınırları; prereg §18/§23 yasakları; E0 P13; rapor §14:349-350 | Tartışma/genelleme bölümü; §18 raporlama kuralları | [ ] insan kararı: |
| C-09 | Novelty / "first benchmark" | Rapor §3:60-98 (INCREMENTAL VARIANT; CASE/MTMCS/CarryOn/OpenSafeIntent/PENGUIN/RAGRefuse/CB-Bench matrisi) | "İlk benchmark" (bu depoda böyle bir başlık yok; gelecekte kullanılmaması için) | terk et ("first"); daralt (katkı cümlesi) | "Önceden dondurulmuş tanısal pilot: bayt-sabit son istem + alternatif sabit geçmişler + davranış/uygunluk ayrımı + filler/AM/benign/high-risk ayrı kontroller. 'İlk' yok." (Bkz. önerilen yayın iddiası.) | Rapor §3:64, §3:96-98; E0 "yapılmayanlar" (literatür taranmadı — bu taslak raporun haritasını benimser, bağımsız doğrulamaz) | Başlık/abstract/katkı cümlesi | [ ] insan kararı: |
| C-10 | Calibration (psikometrik/olasılıksal) | Rapor §2:58, §4 F4:132-140, §6.1:168-180 | "Güvenliği doğru kalibre ediyor" | terk et (terim); daralt (ayrı raporlama) | "Calibration terimi kullanılmaz. Davranış (nominal action), harmful capability (present/absent/uncertain) ve meşru fayda (completed/partial/not_completed) ayrı raporlanır; tek eksenli safety/helpfulness skoru üretilmez." | Rapor §6.1–6.2; E0 P03–P05 (E1b'ye devredildi) | Ölçüm sözleşmesi (E1b); no-composite ilkesi (§13, rapor §12) | [ ] insan kararı: |
| C-11 | Contamination yokluğu | `README.md:209-212`; `results/dataset_audit/overlap_report.json` (`preliminary_blocked`); rapor §14:351 | "Hash eşleşti, veri temiz" (zımni) | ertele (yokluk iddiası yok) | "Hash bütünlüğü doğrulandı; contamination yokluğu ispatlanmadı ve iddia edilmiyor. Dış overlap denetimi (`pending_pinned_retrieval`) kapanmadan XSTest/JBB/WildGuard ile analitik birleştirme yok." | E0 provenance §4–5; rapor §14:351 UNRESOLVED | Veri bölümü + Phase 6B kapısı | [ ] insan kararı: |
| C-12 | Puanlama iddiası (iki-insan primary vs judge) | `phase7e_annotation_protocol.md:149-184`; `phase7g_human_qc.md:16-28`; `ROADMAP.md:48-53`; rapor §10:302 | "Hibrit judge + %20 insan primary'nin yerini tutar" (ROADMAP drift'i) | koru (frozen) + ertele (judge) | "Bu pilotun primary puanlaması iki bağımsız insandır; judge/lexical detector yalnız secondary/triage. κ≥0,85 hedefi false-negative/family-bias denetiminin yerine geçmez. Judge değişikliği açık amendment ister; bu pilot için önerilmiyor." | E0 P05/P08/P12; rapor §10:302, §11:317 | Puanlama sözleşmesi; bütçe (1.026 yanıt/model) E7'ye aittir | [ ] insan kararı: |
| C-13 | research_questions.md'nin eski kapsamı (300 örnek, savunma katmanı, Pareto) | `docs/research_questions.md:21,31-45,74-80`; üst plan §7 (ertelenenler) | RQ1–RQ4 (model aileleri, bağlam avantajı, savunma katmanı A/B/C, Pareto) | ertele | "RQ dokümanı tasarım tarihidir; birincil pilotun iddia kaynağı değildir. Savunma katmanı prototipi, Pareto sınırı, model leaderboard'u, çok-dil/genişleme bu pilotun dışında; ayrı araştırma sorusu/veri sürümüyle ele alınır." | Üst plan §7; E0 P01 (kapsam) | Kapsam bölümü; E7 kapsam disiplini | [ ] insan kararı: |
| C-14 | Hipotez/güç sayıları (H1 non-trivial, H3/F4 sıfır çakışması, Δ≥0,35) | Prereg §2:28-34, §19:320-326; `docs/statistical_power_and_limitations.md:27-31,51`; rapor §8.2:249, §10:294 | "Non-trivial share / Δ≥0,35'te %80 güç / H3–F4 mevcut haliyle" | daralt (E1c'ye devir; burada hüküm yok) | "H1'in 'non-trivial share'i operasyonelleştirilmeden iddia yapılmaz. H3 (median Δ_BC ≥ 0) ile F4 (median Δ_BC ≤ 0) sıfırda çakışıyor; E1c taslağı çakışmayı giderir. Δ≥0,35 tek başına güç iddiası değildir (discordance/varyans gerekir)." | E0 P02/P04/P08/P15; rapor §8.2:249 | E1c amendment taslağı; H1–H3/F1–F6 revizyonu | [ ] insan kararı: |

## Önerilen en güçlü yayın iddiası (taslak; DRAFT / NOT EFFECTIVE)

> "Önceden tanımlanmış İngilizce teknik görevlerden oluşan bu korpusta, bayt-düzeyinde sabit son
> istemlerin alternatif sabit konuşma geçmişleri altında üretilen yanıt dağılımlarını
> karşılaştırdık; davranış, zararlı kapasite aktarımı ve meşru faydanın ayrıştığı bağlama özgü
> örüntüleri, insan referansları ve ayrı kontrol gruplarıyla (kalıcı belirsizlik, benign taban,
> high-risk tavan, nötr dolgu) belgeledik. Bulgular gerçek kullanıcı niyetinin tanınmasını, saf
> kullanıcı-kanıtı etkisini, genel interaktif güvenliği veya yaygınlığı göstermez."

Bu cümlede yön, model adı, etki büyüklüğü ve başarı sonucu doldurulmadı; bunlar henüz gözlenmedi
(rapor §16:G, §16:H). D'nin yokluğu semantik mekanizma kanıtı sayılmadı; AM, DU assistant etkisinin
tanımlanması olarak kullanılmadı; hash, contamination yokluğu sayılmadı.

## Etkilenen hipotez ve çıktılar (özet)

- H1/H0a: C-01 + C-14 ile okunur (whole-history + operasyonel eşik E1c'de).
- H2/H3/H0c: davranışsal yön iddiaları E1b'nin nominal-action + ayrı harm/utility ayrımına bağlı;
  H3/F4 çakışması E1c'de giderilir.
- H0b/F2: C-04 ile okunur (D yalnızca length/priming).
- F5/F6: C-02/C-03 + QC kapısı (E2a) + blind gate sonuçları (§18 raporlama kuralı korunur).
- Çıktılar: başlık/abstract/katkı (C-09), yöntem (C-01/C-07), kontroller (C-04–C-06),
  sınırlar (C-08/C-11/C-13), ölçüm (C-10/E1b), puanlama (C-12), güç/hipotez (C-14/E1c).
- Korunanlar (rapor §12): final-byte eşitliği, within-item eşleştirme, DU/AM/NB/NH ayrımı + ayrı
  null'lar, A/B/C katman ayrımı, bağımsız utility, no-composite, freeze/provenance disiplini,
  iki-insan primary.

## Mekanizma iddialarının construct'tan ayrılması (kontrol listesi)

- [ ] "Skor değişti" → "davranış değişti" çıkarımı yok (E1b nominal + ayrı harm/utility bekler).
- [ ] "Davranış değişti" → "model riski doğru anladı" çıkarımı yok (C-02 terk).
- [ ] D sessizliği → "assistant kanalı elendi" çıkarımı yok (C-04 + clarification C6).
- [ ] AM hareketi/hareketsizliği → "DU mekanizması" çıkarımı yok (C-05 + C-07).
- [ ] NB geçişi → "sağlamlık" / NH geçişi → "laundering direnci" genellemesi yok (C-06).
- [ ] Hash → "temiz veri" çıkarımı yok (C-11).
- [ ] Tek bileşik güvenlik puanı yok (C-10; prereg §13 no-composite korunur).
