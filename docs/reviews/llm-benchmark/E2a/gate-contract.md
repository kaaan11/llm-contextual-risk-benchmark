# E2a — Phase 7G kapı ve durum geçiş sözleşmesi (gate-contract)

**Statü: UYGULANAN KOD + KANIT.** Bu paket frozen kuralları uygular (implementation drift
correction); yeni rubrik, D alanları ve Layer-B şeması E2b/E2c kapsamıdır. Bilimsel karar
içermez; frozen `FAIL is never waived` kuralı uygulanır, kural değişikliği tasarlanmaz.

- Kök kural 1 (frozen `docs/phase7e_annotation_protocol.md` §2.4): isolated gate FAIL'u
  REVISE/REJECT'e gönderir; **never waived**.
- Kök kural 2 (araştırmacı kararı R2): iki bağımsız kör rater zorunludur; ADJUDICATED olmadan
  final KEEP yoktur.

## 1. Kapı matrisi (fail-closed)

`S` = blind annotation_status, `G` = gate_result. `record_context` = bağlam kaydı,
`record_decision(KEEP)` = final KEEP, `validator` = `validate()` onay değişmezleri,
CLI-list = sihirbaz listeleme, CLI-keep = sihirbaz KEEP teklifi.

| S / G | record_context | record_decision KEEP | validator (onaylıysa) | CLI-list | CLI-keep teklifi |
| --- | --- | --- | --- | --- | --- |
| PENDING / — | RET | RET | hata (anotasyonsuz onay) | listelemez | — (kayıt yok) |
| PARTIAL_ONE_RATER / — | RET | RET | hata (two-rater) | listelemez | — |
| DISAGREEMENT_PENDING / — | RET | RET | hata (two-rater) | listelenir* | teklif etmez |
| ADJUDICATED / PASS | AÇIK | AÇIK (diğer kapılar tamamsa) | temiz | listeler | teklif eder |
| ADJUDICATED / REVIEW | AÇIK | AÇIK (diğer kapılar tamamsa) | temiz | listeler | teklif eder |
| ADJUDICATED / FAIL | AÇIK (context review yapılır; F6 bilimsel sonuçtur) | RET (never waived) | hata (never waived) | listeler | teklif etmez |

`*` CLI-list = bağlamı bekleyenler değil karar bekleyenlerdir; karar sihirbazı tüm
PENDING'leri listeler ama KEEP'i koşullara bağlar.

## 2. Ortak sınır (tek implementasyon, üç katman)

`scripts/apply_phase7g_annotations.py` içindeki saf (I/O'suz, mutasyonsuz) fonksiyonlar:

- `blind_item_eligible_for_context(blind_item) -> (bool, reason)`: ADJUDICATED + iki slot
  kanıtı (valence + reviewer + timestamp) + adjudicated valence + (uzlaşma | gerekçeli
  adjudication) ister. Eksik provenance reddedilir.
- `blind_keep_blockers(blind_status, gate_result) -> [reasons]`: PENDING/PARTIAL/disagreement
  + `gate_result == FAIL` engellerini üretir; boş liste = blind kapısı geçer.
- `keep_eligibility(qc_item, blind_status, gate_result) -> (bool, reasons)`: blind engelleri +
  review COMPLETE + structural + safety birleşimi (CLI teşhir/karar sınırı).
- `blind_item_for` / `blind_gate_for`: fail-closed kör-kayıt bulma (`QCError`, `StopIteration`
  değil); bilinmeyen eşleme listelenmez, validator ayrıca işaretler.

Kullanıcılar: `record_context` (ret), `record_decision` KEEP dalı (ret),
`validate()` onay değişmezleri (hata), `review_context.get_pending_context_items` (liste),
`decide_phase7g` KEEP teklifi + kapı teşhiri (aynı sınır). Eski gevşek `_blind_submitted_for`
kapı olarak kullanılmaz (tarihsel "submitted" anlamıyla korunur, docstring işaretli).

## 3. FAIL kablolaması

- Writer: KEEP dalında `blind_keep_blockers` — FAIL `QCError("... never waived ...")`
  üretir; structural/safety kontrolleri aynı kalır (mesajlar korunur).
- Validator: onaylı kayıtta FAIL `approved despite isolated blind gate FAIL` hatası üretir;
  dosyadan yüklenen mevcut yanlış durum böylece yakalanır.
- CLI: karar sihirbazı kapı sonucunu gösterir (`gate_result` + `gate_flag`) ve FAIL'de KEEP
  teklif etmez (REVISE/REJECT açık).
- Context review FAIL-gate'li maddede AÇIKTIR (kapı sonucu bilimsel kayıttır, otomatik ret değil).

## 4. Ret bütünlüğü (no-mutation)

`_atomic` sarmalayıcı: `record_blind/record_context/record_adjudication/record_decision`
herhangi bir hatada çağrıcının nesnelerini aynen geri yükler ve hatayı yeniden fırlatır.
Dosya/snapshot/history çağrıcılar tarafından yalnız başarı sonrası yazıldığından ret işlemi
hiçbir kalıcı veya bellek-içi iz bırakmaz. Toplu (batch) çağrıda ilk payload'ın kısmi
uygulanması geri alınır.

## 5. Bağımsızlık beyanı (non-claim)

Farklı reviewer ID'leri bilişsel bağımsızlığın KANITI diye raporlanmaz: kodda yalnız süreç
kontrolü vardır (aynı ID iki slotta reddedilir); anonim rol senaryosunda bağımsızlık insan
araştırmacının süreç beyanıdır. Bu dosyada veya kod çıktılarında aksi iddia yoktur.

## 6. Test stratejisi ve fixture etiği

- Negatif yollar: canlı PENDING/PARTIAL durumları (deepcopy) + alansal minimal fixture'lar
  (status/gate alanları; rater atfı, timestamp, history YOK). Validator modülünün belgesel
  amacı ("synthetic violations") budur; kayıt/atfetme yapılmaz, diske yazılmaz.
- Tutarlılık: her yapısal blind durumunda writer-ret ⟺ validator-hata
  (`tests/test_phase7g_gates.py::FailGateTests::test_writer_validator_agree_on_blind_states`).
- Mutation-yok: ret sonrası derin-eşitlik (`test_refused_context_changes_nothing`,
  `test_writer_refusal_changes_nothing`, `test_batch_refusal_is_atomic`).
- CLI: liste dışlama (canlı PARTIAL) + `keep_eligibility` birim testleri.
- Mevcut `record_blind` valence literalleri yalnız suite'in yerleşik F-06 fixture örüntüsünde
  (bellek-içi, role "r", yazılmaz) kullanılır; yeni insan-semantikli pozitif yol uydurulmadı.
- **İnceleyici kabul örneği (açık):** gerçek insan provenance'lı pozitif iki-rater geçişi
  (canlı ADJUDICATED → context → KEEP) ancak gerçek anotasyonla sınanabilir; uydurulmadı.

## 7. Değişen dosyalar

- `scripts/apply_phase7g_annotations.py`: ortak kapı fonksiyonları + FAIL reddi + `_atomic`.
- `scripts/validate_phase7g_review.py`: ortak sınırdan FAIL/two-rater hata üretimi.
- `scripts/review_context.py`: listelemede ortak kapı.
- `scripts/decide_phase7g.py`: ortak `keep_eligibility` + kapı teşhiri.
- `tests/test_phase7g_qc.py`, `tests/test_remediation_regressions.py`: gevşek kapıyı kodlayan
  3 test E2a davranışına güncellendi.
- `tests/test_phase7g_gates.py`: 22 yeni kabul testi.
- Üretim QC/audit JSON'ları, mühürlü belgeler, stimulus, insan rating'leri değişmedi.
