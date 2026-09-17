# E2a-R1 — Phase 7G kapı ve durum geçiş sözleşmesi (gate-contract)

**Statü: UYGULANAN KOD + KANIT (E2a revizyonu).** `../E2a/gate-contract.md` değişmedi; bu dosya
R1–R4 düzeltmelerini içeren güncel sözleşmedir. Frozen kuralları uygular; yeni rubrik, D
alanları ve Layer-B şeması E2b/E2c kapsamıdır. Bilimsel karar içermez.

- Kök kural 1 (frozen §2.4): FAIL REVISE/REJECT'e gider; **never waived**.
- Kök kural 2 (R2): iki bağımsız kör rater; ADJUDICATED olmadan final KEEP yok.

## 1. Kapı matrisi (fail-closed, kanıt-temelli)

`record_context` = bağlam kaydı, `record_decision(KEEP)` = final KEEP,
`validator` = onay + ordering değişmezleri, CLI-list/CLI-keep = sihirbazlar.
Parantez: hangi kanıtın eksik olduğu.

| Blind kayıt | record_context | record_decision KEEP | validator | CLI |
| --- | --- | --- | --- | --- |
| PENDING | RET | RET | hata (sıralama + onaysız anotasyon) | listelemez |
| PARTIAL (canlı dahil) | RET | RET | hata (two-rater) | listelemez |
| DISAGREEMENT çözümsüz | RET | RET | hata (two-rater) | KEEP teklif etmez |
| ADJUDICATED, provenance eksik / aynı ID | RET | RET | hata (two-rater) | KEEP teklif etmez |
| ADJUDICATED, gate eksik/bilinmeyen/uyuşmaz | RET (kapı değilse AÇIK*) | RET | hata (kapı) | KEEP teklif etmez |
| ADJUDICATED, gate FAIL (tutarlı) | AÇIK (F6 bilimsel sonuçtur) | RET (never waived) | hata (never waived) | KEEP teklif etmez |
| ADJUDICATED, gate PASS/REVIEW (tutarlı) | AÇIK | AÇIK (diğer kapılar tamamsa) | temiz | teklif eder |

`*` Context kapısı gate sonucuna bakmaz; yalnız kayıt bütünlüğüne (ADJUDICATED + kanıt).
Gate FAIL context review'u engellemez.

## 2. Ortak sınır (tek implementasyon, dört tüketici)

`scripts/apply_phase7g_annotations.py` içindeki saf fonksiyonlar:

- `blind_item_eligible_for_context(blind_item) -> (bool, reason)`: ADJUDICATED + iki
  kanıtlı slot (valence + **dolu reviewer_id** + timestamp) + farklı ID'ler + adjudicated
  valence + (uzlaşma | gerekçeli adjudication). Rol tek başına kimlik değildir.
- `keep_gate_blockers(blind_item, category) -> [reasons]`: yukarıdaki kanıt + gate'in
  mevcut, bilinen (`PASS/REVIEW/FAIL`) ve `evaluate_gate(adjudicated_valence, category)`
  ile tutarlı olması + KEEP için `PASS/REVIEW` zorunluluğu. Status/gate ikilisi tek başına
  ASLA yeterli değildir (E2a'daki `blind_keep_blockers` kaldırıldı).
- `keep_eligibility(qc_item, blind_item, category)`: blind kapısı + review COMPLETE +
  structural + non-FAIL safety (CLI teşhir/karar sınırı).
- `blind_item_for` / `blind_gate_for` / `category_for`: fail-closed bulma
  (`QCError`; `expected_valence` bilerek KULLANILMAZ — Layer A hipotezidir).

Tüketiciler: `record_context` (ret), `record_decision` KEEP dalı (ret),
`validate()` onay + ordering değişmezleri (hata), `review_context` listesi,
`decide_phase7g` teklifi + kapı teşhiri (aynı sınır). Eski gevşek `_blind_submitted_for`
kapı olarak kullanılmaz.

## 3. FAIL / eksik / bilinmeyen / uyuşmaz kapı

- Tutarlı FAIL → writer `QCError("... never waived ...")`; validator
  `approved despite isolated blind gate FAIL`; CLI teklif etmez.
- Eksik (`None`), bilinmeyen değer, `stored != recomputed` → ayrı ret/hata mesajları
  (sessiz PASS yok). Mesaj kodları: `isolated gate result missing`,
  `isolated gate result unknown: <value>`,
  `isolated gate mismatch: stored <s> != recomputed <e>`.
- Kategori eşlemesi yoksa kapı doğrulanamaz → ret/hata (fail-closed).

## 4. Validator ordering (R3)

Context `NOT_STARTED` dışındaysa yüklenen blind kaydın TAM kanıtı aranır: PENDING, PARTIAL,
çözümsüz disagreement, eksik provenance, aynı-ID ve eşlemesiz durumlar hata olarak raporlanır.
Writer'ın üretemediği state diskten gelirse yakalanır.

## 5. Ret bütünlüğü (korundu)

`_atomic`: rette çağrıcı nesneleri geri yüklenir, hata yeniden fırlatılır; dosya/snapshot/
history yalnız başarı sonrası yazılır. Toplu geri alma dahil.

## 6. Bağımsızlık beyanı (non-claim, korundu)

Farklı ID'ler bilişsel bağımsızlığın kanıtı diye raporlanmaz; süreç kontrolüdür
(`same reviewer_id` iki slotta ret). Canlı
BLIND-001 anotasyonu rol-only (ID yok) olduğundan kapıyı ASLA geçemez — ID/annotasyon
uydurulmadı; eksik kayıt fail-closed kalır; karar insan araştırmacınındır.

## 7. Test stratejisi ve fixture etiği

- Negatif yapısal ihlal vektörleri: canlı PENDING/PARTIAL, boş-slot + el-statusu, aynı-ID,
  eksik/bilinmeyen/uyuşmaz gate. Vektörlerde SYNTHETIC-ID'ler ve yer tutucu slot valence'ları
  insan Semantiği taşımaz; gate yeniden hesabı için gereken tek adjudicated literal açık
  işaretlidir; rater atfı/timestamp/history YOKTUR, diske yazılmaz.
- Tutarlılık: her yapısal durumda writer-ret ⟺ validator-hata (7 durum).
- Mutation-yok (derin-eşitlik) + batch atomikliği korunur.
- **Açık kabul örnekleri:** gerçek insan provenance'lı pozitif iki-rater geçişi ve tam
  adjudication akışı (E2E) ancak gerçek girdilerle sınanabilir; uydurulmadı.

## 8. R1-delta (E2a → E2a-R1)

Kaldırılan: status/gate-ikilisi `blind_keep_blockers` (ölü sınır). Eklenen: ID zorunluluğu +
farklılık kontrolü, gate yeniden-hesap tutarlılığı, validator ordering kanıtı, kategori araması.
Davranış farkı: rol-only ADJUDICATED kayıtlar (canlı BLIND-001 dahil) artık kapıdan geçemez;
gate'siz/bilinmeyen/uyuşmaz kapı KEEP'i reddeder. E2a'nın PARTIAL-ret, FAIL-ret ve atomicity
davranışları aynen korundu.

## 9. Değişen dosyalar

- `scripts/apply_phase7g_annotations.py`: kanıt kapıları + `_atomic` (korundu).
- `scripts/validate_phase7g_review.py`: onay + ordering kanıt değişmezleri.
- `scripts/review_context.py`, `scripts/decide_phase7g.py`: aynı sınır (yeni imzalar).
- `tests/test_phase7g_gates.py`: 31 kabul testi (5 karşıörnek grubu dahil).
- `tests/test_phase7g_qc.py`, `tests/test_remediation_regressions.py`: E2a davranış
  güncellemeleri korundu (bu turda ek değişiklik gerekmedi).
- Üretim QC/audit JSON'ları, mühürlü belgeler, stimulus, insan rating'leri değişmedi.
