# E3a — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker envanteri; insan QC kararı bekleniyor).**
Görev: [E3a briefi](../../../llm-benchmark-E3a-task.md).
Üst plan: [değerlendirme ve eylem planı](../../../llm-benchmark-assessment-and-plan.md) §E3a.
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).
Önkoşul: E0 kabulü (`../E0-acceptance.md`).

## Sonuç

Raporun AM002/referent/DU004/D-priming örnekleri tam-korpus (50/171) ölçülü envantere
dönüştürüldü: 19 aday (7 T-XCOND, 6 T-REF, 5 T-DHINT-LEX, 1 T-DHINT-HUMAN), hepsi REVIEW
(insan kuyruğu). Metin düzeltme, REVISE/REJECT kararı ve yeni sürüm YOK.

- Yapısal bütünlük 50/50 geçti (final-byte, tur, D-strateji); T-STRUCT adayı yok.
- Ayrımlar korundu: bütünlük≠coherence; referent≠risk; D-hareketi≠mekanizma; stance farkı
  bilinen sınırlama (kusur değil); bayt≠token (tolerans AÇIK).
- Örnekten toplama tahmin YOK; taranan popülasyon + kural her satırda açık.
- Otomasyon hüküm vermez: DU004 leksik-taramada negatiftir (taramanın sınır kanıtı).

## Değişen dosyalar (yalnız bu dizin)

- `stimulus-issues.md`: yöntem + bütünlük + 19 satır aday tablosu + ayrımlar + kuyruk.
- `stimulus-issues.json`: makine-okunur tablo (meta + structural + measurements + findings).
- `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`,
  `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256`, `logs/`.
- v1 baytları, QC/audit kayıtları, kod, testler değişmedi. Tarama betiği geçici dizinde
  (`/tmp/opencode/e3a_scan.py`); kurallar `stimulus-issues.md` yöntem tablosunda tam tanımlı.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `.venv pytest --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Deterministik taramalar (50/171, 19 aday; v1'e yazım yok) | `logs/03-stimulus-scans.sh.stdout` | 0 |
| 04 | Hedefli salt-okunur testler (`test_phase7f_stimulus.py`) | `logs/04-targeted-tests.sh.stdout` | 0 |
| 05 | `git diff --check` + yazım kontrolü (stimulus/audit değişmedi) | `logs/05-diff-check.sh.stdout` | 0 |
| 06 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/06-link-check.sh.stdout` | 0 |
| 07 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/07-run-outputs.sh.stdout` | 0 |

Not: 03 sonrası `commands.jsonl` içindeki `combined` yolu yazım hatası (E2a) düzeltildi;
kayıtların komut/zaman/exit/log içeriği değişmedi.
`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz.

## Sınırlılıklar

- Adaylar hüküm değildir; naturalness/safety/E3b kararları insanındır.
- Tokenizer profili yok → token toleransı AÇIK. Dış literatür taranmadı.

## Devam

E3a burada durur; E3b'ye geçilmez. Sıradaki önkoşul: ana inceleyicinin `../E3a-acceptance.md`
kararı + araştırmacının E3b yetki kararı (koruma/REVISE/REJECT, ayrı brief).
