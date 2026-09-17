# E2a-R1 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker kod teslimi; ana inceleyici kabulü bekleniyor).**
Görev: [E2a-R1 briefi](../../../llm-benchmark-E2a-r1-task.md).
Önkoşul: `../E2a-acceptance.md` (REVISION REQUIRED; R1–R4).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E2a kapıları status alanından bağımsız, gerçek kayıt dayanaklarına bağlandı; context
writer/list, KEEP writer/CLI ve validator aynı kanıtı kullanıyor. E2b/E2c rubriği ve üretim
annotation verisi değişmedi.

- Ortak girdi status/gate ikilisi değil: iki slot + provenance + farklı kalıcı ID'ler +
  agreement/adjudication akışı + gate tutarlılığı (`evaluate_gate` yeniden hesabı).
- Rol tek başına kimlik değildir; aynı-ID reddedilir; eksik kayıt fail-closed (canlı BLIND-001
  dahil — ID uydurulmadı, karar araştırmacınındır).
- Validator: context açıksa tam kanıt arar (PENDING/PARTIAL/çözümsüz/provenance/aynı-ID/eşlemesiz
  hata); KEEP yalnız tutarlı PASS/REVIEW ile mümkün.
- Ret mutation-yok + FAIL yasağı korundu. 381 test geçti (31 gates); diff-check temiz.

## Değişen dosyalar

- Kod: `scripts/apply_phase7g_annotations.py`, `scripts/validate_phase7g_review.py`,
  `scripts/review_context.py`, `scripts/decide_phase7g.py` (yeni imzalar, ölü status-only
  helper kaldırıldı).
- Test: `tests/test_phase7g_gates.py` (31 test; 5 karşıörnek grubu).
- Kanıt: `gate-contract.md`, `revision-map.md`, `README.md` (bu dosya), `comparisons.md`,
  `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`,
  `logs/`.
- `../E2a/` kanıtı, üretim QC/audit JSON'ları, mühürlü belgeler, stimulus, insan rating'leri
  değişmedi. Testler audit dosyalarına yazmadı.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `.venv pytest --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Hedefli testler (gates/qc/tooling/remediation) | `logs/03-targeted-tests.sh.stdout` | 0 |
| 04 | Tam offline suite | `logs/04-full-suite.sh.stdout` | 0 |
| 05 | Validator CLI'ları + `git diff --check` + yazım kontrolü | `logs/05-validators-diff.sh.stdout` | 0 |
| 06 | Frozen hashler + kapı-conformance + karşıörnek kapsam sayımı | `logs/06-frozen-hashes.sh.stdout` | 0 |
| 07 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/07-link-check.sh.stdout` | 0 |
| 08 | `run-outputs.sha256` üretimi (belgeler + diff + log stdout'ları; kendi üretim logu hariç) | `logs/08-run-outputs.sh.stdout` | 0 |

## Sınırlılıklar

- Pozitif iki-rater geçişi (gerçek provenance) + tam adjudication E2E inceleyici kabul örneği
  olarak açık; sentetik insan girdisi üretilmedi.
- E1b/E1c insan bilimsel kararları bekliyor; ölçüm sözleşmesi değişmedi.

## Devam

E2a-R1 burada durur. Sıradaki önkoşul: ana inceleyicinin `../E2a-r1-acceptance.md` kararı.
