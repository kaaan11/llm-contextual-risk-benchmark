# E1c — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker taslağı; insan araştırmacı + ana inceleyici kararı bekleniyor).**
Görev: [E1c briefi](../../../llm-benchmark-E1c-task.md).
Üst plan: [değerlendirme ve eylem planı](../../../llm-benchmark-assessment-and-plan.md) §E1c.
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).
Önkoşul: E0 kabulü + E1a/E1b teslimleri (`../E0-acceptance.md`, `../E1a-acceptance.md`,
`../E1b-r6-acceptance.md` — E1b zinciri worker-tamam, insan bilimsel kararı bekliyor).

## Sonuç

Eski/önerilen ölçüm sözleşmesi farkı pre-evaluation amendment taslağına dönüştürüldü.
Etkin protokol değildir; `rules_changed=false` açıklamasına eklenmez; mühürlü dosyalar değişmez.

- `estimand-contract.md`: birincil E-act/E-harm/E-util (madde-eşit B/C, DU=30; AM/NB/NH/DU-D ayrı,
  havuzlama yok), ikincil error-asymmetry McNemar + modal + D kohortu + Fisher, tekrar/missing/
  duplicate/error/exclusion + applicability/sıfır-payda politikası, test/CI varsayımları +
  multiplicity, CI/alfa/eşik karar seçenekleri, 3 karşıörnek + beklenen sonuçlar.
- `legacy-to-proposed.md`: 15 kural satırı (koru/kaldır/seçenekli) + arşiv kaydı.
- `amendment-draft.md`: sürümlü taslak (v1.0.3-draft yer tutucu), fark listesi, hipotez geçişi,
  yürürlük koşulları, boş imza.
- Mode ikincil/sınırlı; McNemar error-asymmetry adlı; ordinal/D-flag/Wilcoxon statüleri açık;
  H3/F4 + eşik dili için somut seçenekler var. Birincil endpoint/alfa/eşik onaylanmış gibi
  seçilmedi (Öneri etiketleri ≠ onay). E5/E6'ya etkin devir yok.

## Değişen dosyalar (yalnız bu dizin)

- `estimand-contract.md`, `legacy-to-proposed.md`, `amendment-draft.md`, `README.md` (bu dosya),
  `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`,
  `run-outputs.sha256`, `logs/`.
- Araştırma belgeleri, mühürlü protokol, stimulus, QC/audit, kod değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Frozen hashler + brief kapsam sayımı (endpoint/ağırlık/havuz-yasağı/karşıörnek/APPOVED-yok) | `logs/03-frozen-hashes.sh.stdout` | 0 |
| 04 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/04-diff-check.sh.stdout` | 0 |
| 05 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/05-link-check.sh.stdout` | 0 |
| 06 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/06-run-outputs.sh.stdout` | 0 |

Test briefte istenmiyor: çalıştırılmadı. `commands.jsonl` içinde çalıştırılmayan komut yoktur;
boş satır yoktur. `run-outputs.sha256` kendi üretim logunu kapsamaz.

## Sınırlılıklar

- Karşıörnek sayıları (p≈1,86×10⁻⁹; 5,75/30; %52,8) raporun hesaplarıdır; bu turda bağımsız
  hesaplanmadı, premise'ler yerelde doğruluydu (E0).
- CI yöntemi/TBD eşikler/α seçilmedi; E1b insan kararları (criterion, D-A/D-B, kategori/alan)
  bekliyor. Dış literatür taranmadı.

## Devam

E1c burada durur. Sıradaki önkoşul: araştırmacının §5 + §4 seçenek kararları ve ana inceleyicinin
`../E1c-acceptance.md` kararı. Onay yoksa taslak tamamlanmış sayılabilir, değişiklik etkin sayılmaz.
