# E2a — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker kod teslimi; ana inceleyici kabulü bekleniyor).**
Görev: [E2a briefi](../../../llm-benchmark-E2a-task.md).
Üst plan: [değerlendirme ve eylem planı](../../../llm-benchmark-assessment-and-plan.md) §E2a.
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).
Önkoşul: `../E0-acceptance.md` (E0 KABUL EDİLDİ).

## Sonuç

Frozen kuralları uygulayan fail-closed QC kapıları düzeltildi: tek-rater sonrası context
açılmıyor; blind gate FAIL olan madde KEEP olamıyor (writer + validator + CLI aynı ortak sınır).
Yeni rubrik/D/Layer-B E2b/E2c kapsamıdır; E2'nin tamamı veya insan QC hazır ilan edilmedi.

- Ortak saf kapılar (`blind_item_eligible_for_context`, `blind_keep_blockers`,
  `keep_eligibility`, `blind_item_for`/`blind_gate_for`); CLI liste + kayıt API'si aynı sınır.
- Ret edilen işlem nesne/dosya/snapshot/history değiştirmez (`_atomic`; toplu geri alma dahil).
- ID farklılığı bağımsızlık kanıtı diye raporlanmaz.
- 372 test geçti (22 yeni `test_phase7g_gates.py` dahil); `git diff --check` temiz; bütünlük korunur.

## Değişen dosyalar

- Kod: `scripts/apply_phase7g_annotations.py`, `scripts/validate_phase7g_review.py`,
  `scripts/review_context.py`, `scripts/decide_phase7g.py`.
- Test: `tests/test_phase7g_gates.py` (yeni, 22 test), `tests/test_phase7g_qc.py`,
  `tests/test_remediation_regressions.py` (gevşek kapıyı kodlayan 3 test güncellendi).
- Kanıt: `gate-contract.md`, `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`,
  `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- Üretim QC/audit JSON'ları, mühürlü belgeler, stimulus, insan rating'leri değişmedi.
  Testler gerçek audit/QC dosyalarına yazmadı (sonrası `git status` temiz).

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `.venv pytest --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Hedefli testler (gates/qc/tooling/remediation: 132 test) | `logs/03-targeted-tests.sh.stdout` | 0 |
| 04 | Tam offline suite (372 test) | `logs/04-full-suite.sh.stdout` | 0 |
| 05 | Validator CLI'ları + `git diff --check` + `git status` (audit yazım kontrolü) | `logs/05-validators-diff.sh.stdout` | 0 |
| 06 | Frozen hashler: composite + stimulus 50/171 + audit prefix + kapı-conformance grepleri | `logs/06-frozen-hashes.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + diff + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

## Sınırlılıklar

- Pozitif iki-rater geçişi gerçek insan provenance'ı olmadan sınanamaz; inceleyici kabul
  örneği olarak açık bırakıldı (`gate-contract.md` §6). Sentetik kör-rater anotasyonu üretilmedi.
- `decide_phase7g` bilinmeyen eşlemede maddeyi atlar (validator ayrıca işaretler); davranış
  `comparisons.md`'de açıklanır.
- E1b/E1c insan bilimsel kararları bekliyor; bu paket ölçüm sözleşmesini değiştirmez.

## Devam

E2a burada durur. Sıradaki önkoşul: ana inceleyicinin `../E2a-acceptance.md` kararı
(kabul şablonuyla). E2b/E2c bu kabulü + ilgili E1 sözleşmesini bekler.
