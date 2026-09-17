# E1c-R1 — Teslim kanıt paketi

Durum: **TAMAMLANDI (worker revizyonu; yeniden inceleme bekleniyor).**
Görev: [E1c-R1 briefi](../../../llm-benchmark-E1c-r1-task.md).
Önkoşul: `../E1c-acceptance.md` (REVISION REQUIRED; R1–R5).
Sözleşme: [worker sözleşmesi](../../../llm-benchmark-worker-contract.md).

## Sonuç

E1c'deki beş blokaj kapatıldı; nominal madde-eşit yaklaşım, legacy ayrımı, karşıörnekler ve
`DRAFT / NOT EFFECTIVE` sınırı korundu. E6a'nın seçim icat etmeden uygulayacağı kapalı taslak
üretildi (seçim noktaları seçenek olarak işaretli).

- **R1:** E-act/E-harm/E-util kapalı pay/payda tablosu; `uncertain`/`partial`/gap/applicability
  davranışları tanımlı; alternatifler seçenek (H-U1/H-U2, H-T1a/H-T1b, D-A/D-B), tek kural yok.
- **R2:** Canonical logical job kimliği + attempt/gözlem ayrımı + E5a normatif ref.
- **R3:** `stratified_by_assistant_stance` zorunlu ekseni; kategori ekseninden ayrı; havuzlama
  yok; sıfır-payda açık rapor.
- **R4:** "Exact CI" vaadi kalktı; O-C1–O-C4 seçenekleri (varsayım/sınır/kapsam); CP tek-oranla sınırlı.
- **R5:** D-A/D-B seçenek tablosu; uygulanan kural YOK; teknik kapılar ayrı.
- **Matematik:** KÖ-1/KÖ-3 deterministik yeniden hesap (stdlib, insansız): p=1.862645149230957e-09;
  E=5.75; P(X≥6)=0.5281675159; KÖ-3 16/14 kurulumu açık.

## Değişen dosyalar (yalnız bu dizin)

- `estimand-contract.md` (v0.2), `amendment-delta.md`, `legacy-delta.md`, `revision-map.md`,
  `README.md` (bu dosya), `comparisons.md`, `commands.jsonl`, `hashes-start.txt`, `hashes-end.txt`,
  `delivery.diff`, `run-outputs.sha256`, `logs/`.
- `../E1c/` kanıtı değişmedi. Frozen belgeler, stimulus, audit/QC, kod, insan rating'leri değişmedi.

## Doğrulamalar (gerçek komutlar; çalıştırılmayan yok)

| # | Komut (özet) | Log | Exit |
| --- | --- | --- | --- |
| 01 | `git rev-parse HEAD`, `status`, `branch`, `log -3` | `logs/01-git-head-status.sh.stdout` | 0 |
| 02 | `python3 --version`, `uv --version` | `logs/02-env.sh.stdout` | 0 |
| 03 | Deterministik matematik (KÖ-1/KÖ-3) + frozen hashler + brief kapsam sayımı | `logs/03-math-frozen.sh.stdout` | 0 |
| 04 | `git diff --check` + `status` + `delivery.diff` üretimi | `logs/04-diff-check.sh.stdout` | 0 |
| 05 | Teslim içi bağlantı kontrolü (final, PASS) | `logs/05-link-check.sh.stdout` | 0 |
| 06 | `run-outputs.sha256` üretimi (belgeler + log stdout'ları; kendi üretim logu hariç) | `logs/06-run-outputs.sh.stdout` | 0 |

Matematik saf stdlib hesaplamadır; insan anotasyonu/model çağrısı yoktur.
`commands.jsonl` içinde çalıştırılmayan komut yoktur; boş satır yoktur.
`run-outputs.sha256` kendi üretim logunu kapsamaz.

## Sınırlılıklar

- Seçenek kararları (endpoint ailesi onayı dahil), CI yöntemi, TBD eşikler, E1b insan kararları
  bekliyor. Karşıörnek mekanizma tasvirleri rapor modelidir; toplu sayılar deterministik doğrulandı.
- Dış literatür taranmadı.

## Devam

Teslimden sonra durulur. Sıradaki önkoşul: ana inceleyicinin yeniden incelemesi.
İnsan kararları `APPROVED` yapılmadı; E5/E6'ya etkin devir yok.
