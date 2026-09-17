# E0 — Provenance ve kapsam ayrımı (provenance-scope)

Beş iddia ayrı tutuldu: hash bütünlüğü, commit aidiyeti, kaynak lisansı, overlap durumu,
contamination yokluğu. Hiçbiri birbirinin yerine kullanılmadı. Blind key kapsamı §6'da;
içerik/hash/mapping bu pakete taşınmadı.

## 1. Hash bütünlüğü (doğrulandı, bu ağaç + bu dosyalar için)

- Protokol composite: `47ae3fed4117639ef2575135a6ca63f000f4fcc8c052c629355f6ccf4bbcfc6f`
  (6 dosya, per-file eşleşti, composite yeniden üretildi; `logs/04-composite.log`).
  Kapsam: `phase7e_preregistration.md`, `phase7e_annotation_protocol.md`,
  `PHASE_7D_EXPERIMENTAL_DESIGN.md`, `PHASE_7D_DESIGN_TABLE.md`,
  `phase7e_pre_evaluation_clarification.md`, `phase7e_design_snapshot.json`.
  AGENTS.md'nin 4'lü mühür listesi bu 6'lı manifestonun alt kümesidir; dördü de eşleşti.
- Stimulus v1: `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`
  (50/171, final-byte 50/50; `logs/05-stimulus.log`).
- Rapor kaynakları: ZIP + Sohbet + 7 geçici dosya hash'leri §baseline-3'te; manifestodaki 7 kayıt eşleşti.
- Rapor alıntı hash'leri (P01–P12): güncel dosyalarla eşleşiyor (`logs/07-cited-hashes.log`).
- Audit history: `phase7e_review_history.jsonl` 51 satır (`e145afed...`), `phase7g_review_history.jsonl`
  5 satır (`23755e0f...`); başlangıç prefix'i korundu, bitişte aynı (`hashes-start/end.txt`).
- Sınır: hash, bu baytların bu hash'lere sahip olduğunu söyler; commit aidiyetini, dış timestamp'i,
  lisansı, overlap'i veya contamination yokluğunu ispatlamaz.

## 2. Commit aidiyeti (doğrulanmadı)

- Beyan: `master / 9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`. HEAD yerelde eşleşiyor.
- ZIP'te `.git` nesnesi yok; kaynak ağacın bildirilen commit'e aidiyeti bağımsız doğrulanamadı.
  Bu, raporun da açıkça yazdığı sınırdır (`LCRB_Kanit_Eki.md:4`).
- HEAD eşleşmesi bütün çalışma ağacının hakem snapshot'ıyla aynı olduğunu kanıtlamaz:
  başlangıçta tracked dirty (`.gitignore`) + 20+ untracked brief/plan dosyası + `uv.lock` vardı.
  Kullanıcı değişiklikleri korundu; E0 bunları düzeltmedi/sahiplenmedi.

## 3. Kaynak lisansı (metadata düzeyi; ham veri yok)

- `results/dataset_audit/source_inventory.json` (`preliminary_blocked`, 3 kaynak):
  XSTest (CC-BY-4.0; 450 prompt; raw kopya yok), JBB-Behaviors (MIT + upstream provenance review gerekli;
  harmful 100 + benign 100 + judge_comparison 300; behavior ≠ jailbreak prompt),
  WildGuardMix (ODC-By + gated AI2 Responsible Use; train 86759 / test 1725; raw commit edilmez).
- `docs/dataset_sources.md` + `configs/phase6b_sources.json` aynı disiplini yineler:
  attribution/revision/retrieval tarihi korunmadan final manifest yok; completion dosyaları alınmaz;
  hassas prompt/completion varsayılan repo dışıdır.
- Sınır: XSTest/WildGuard için immutable revision yakalanmadı; WildGuard native sample ID belgelenmedi;
  exact counts pinned retrieval bekler. Lisans izni upstream koşulları otomatik çözmez.

## 4. Overlap (kısmi kanıt; final havuz yok)

- İç overlap: `stimulus_overlap_report.json` — `dataset/pilot/records.jsonl` vs
  `dataset/pilot/multiturn/records.jsonl` (768 segment); exact 0, normalised 0, high-similarity 0
  (Jaccard eşiği 0,60). Public benchmark metni repoda vendored olmadığı için dış corpus
  karşılaştırılamadı.
- Dış overlap: `overlap_report.json` (`preliminary_blocked`) — JBB judge_comparison–XSTest belgeli
  alt-küme ilişkisi + JBB upstream kompozisyonu (AdvBench %18, TDC/HarmBench %27, Original %55)
  kayıtlı; XSTest/JBB/WildGuard pairwise exact/normalised denetimleri `pending_pinned_retrieval`.
  Sonuç cümlesi: pinned retrieval + pairwise check olmadan nihai bağımsız örnek havuzu ilan edilemez.
- Rapor §14–15'teki `overlap 0` ifadesi iç stimulus raporunun bulgusudur; dış overlap kapanmış değildir.
  Geniş araştırma ertelendi (üst plan §7).

## 5. Contamination yokluğu (ispatlanmadı; bulunmadı da)

- Bu inceleme contamination bulmadı; yokluğunu da kanıtlamadı. Hash ≠ commit authentication ≠
  contamination-free (rapor §14 tehdidi; E0'da `açık` bırakıldı).
- Public seed dataset veya ortak LLM üretim kaynağı overlap yaratabilir; native sample ID belirsizliği
  (`source_inventory.json` limitations) provenance tamamlanmadan kapatılamaz.
- Gerekli kapı: overlap audit P1, geniş contamination çalışması P4 (ertelendi). Pilot conclusions
  prevalence/population genellemesi yapmaz (prereg §18).

## 6. Blind key kapsamı (varlık/paketleme; içerik yok)

- `results/dataset_audit/phase7g_blind_key.json` yerelde mevcuttur (mühürlü eşleme dosyası).
  Bu, S02'deki paket eksikliğinin yerelde dosyanın bulunmadığı anlamına gelmediği kaydıdır.
- Bu pakete içerik, SHA-256/hash, mapping satırı, blind_id↔research_item_id eşleşmesi,
  kategori/valence bilgisi taşınmadı. Bitiş envanterinde yalnız `exists=true` yazıldı
  (`hashes-start/end.txt` notu).
- Anahtar Phase 7G kör anotasyonları sunulmadan açılmaz (`phase7g_human_qc.md:39`).
