# Plan y estado — Track 1

Versión publicable (estrategia y método). Sin genotipos ni coordenadas de
candidatas — eso vive en `notes/private/`.

## Dónde estamos (2026-08-30) — ENVÍO #1: SCORE PERFECTO

**Track 1, submission 1 (equipo IAN-SANTIAGO-MVA): Rank points 100/100, F-max
1.000, "full match at rank 1".** Los dos alelos BUB1B son la respuesta clínica
confirmada:

- **Alelo #1:** truncante en BUB1B, ClinVar Pathogenic/Likely_pathogenic para
  "Mosaic variegated aneuploidy syndrome 1", LOFTEE HC, ultra-raro, CADD 36.
- **Alelo #2:** missense raro en BUB1B (último exón), ausente de gnomAD,
  AlphaMissense 0.92. **Confirmado correcto por el leaderboard** — no era críptico,
  era llamable en el VCF estándar.

Implicancias:

- **El score automático de Track 1 ya está al máximo.** No conviene gastar más
  envíos (solo cuenta el mejor; quedan 5 en reserva). El FAQ del hackathon avisa
  que hay muchos scores perfectos → **el automático es piso, no diferenciador.**
- **Fase 2 (bajar 85 GB, realinear, MEI/SV/splicing) YA NO es necesaria para
  encontrar la variante.** Podría servir solo para *reforzar el writeup* (confirmar
  fase con reads).
- Lo que decide el puesto ahora: **(a) el methods write-up** (lo juzga un panel
  por rigor y profundidad) y **(b) Track 2** (drug repurposing) si lo hacemos.

**Lectura honesta:** de "apuesta a medias" a **respuesta correcta y completa en
~2 días**. Pero el techo ya no depende de la variante — depende de cuán bien
escrito y fundamentado esté el informe frente a las otras decenas de equipos que
también sacaron 100, y de si encaramos Track 2. ~40 % del camino hacia un buen
puesto; el trabajo restante es de comunicación y profundidad, no de pipeline.

## Próximos pasos por ROI (reordenado tras el envío #1)

1. **Pulir el methods write-up** — es lo único que separa entre los 100/100.
   Profundizar: mecanismo BUB1B/BubR1 y el checkpoint de ensamblaje del huso;
   en qué dominio cae el residuo del missense (kinasa / unión a cinetocoro);
   clasificación ACMG de los dos alelos; argumento de fase (trans); y una
   pantalla de hallazgos secundarios (lista ACMG SF).
2. **Confirmar fase con reads** — ahora solo para rigor del informe: bajar el
   BAM/región de BUB1B de los FASTQ, phasing read-backed de los dos alelos.
   (No cambia el score, sí la solidez del writeup.)
3. **Decidir Track 2** — mecanismo ya cerrado (BUB1B LoF → disfunción del SAC →
   aneuploidía → predisposición a cáncer). Track 2 = informe de drug repurposing
   + video de 3 min, 3 envíos por equipo, lo juzga panel experto. Es la otra
   mitad del premio y tenemos la base hecha.
4. **Exomiser/LIRICAL real** (Java + datos hg38) — para ACMG formal en el writeup.
5. **Fase 4:** Snakemake/Nextflow del pipeline + writeup reproducible.

> Nota de mecánica: el `proband_id` que exige el scorer es literalmente
> `PROBAND01` (no el nombre de muestra del VCF).

## Fases (del README)

| Fase | Qué | Rinde |
|---|---|---|
| 1 | Filtrado VCF sobre panel + priorización por fenotipo (Exomiser/LIRICAL) | 1er alelo, ~50 pts |
| 2 | Reads: SV, elementos móviles (MELT/xTea), splicing intrónico (SpliceAI/Pangolin) | 2º alelo |
| 3 | Calibración de `epcr` para F-max + hallazgos secundarios | |
| 4 | Repo reproducible (Snakemake/Nextflow) + writeup de métodos | |

## Equipo / repo

- Repo pensado para ser público, pero **privado hasta que se levante el embargo**
  de publicación (`DATA_HANDLING.md`). Compartir con integrantes vía GitHub
  privado.
- Cada integrante: su propio acceso al dataset en Hugging Face, su propia copia.
  **No se comparten datos, ni entre nosotros** (sin Drive, sin scp, sin bucket).
- Se colabora por código. Antes de cada commit: `git status` +
  `git check-ignore`.

## Envíos registrados

| Track | Fecha | Quién | Resultado |
|---|---|---|---|
| 1 | 2026-08-30 | santiago-rodriguezs (#1) | 100/100 rank points, F-max 1.000, full match at rank 1 |
| 2 | 2026-10-23 | santiago-rodriguezs (#1 del equipo) | Recibido. Reporte `track2/IAN-SANTIAGO-MVA_track2_report.pdf`, video https://youtu.be/d7Gki3xZp8s, repo público. Juzgamiento ~2–3 meses. |

Track 2 acepta un solo envío por equipo: Ian no debe enviar.

## Después del cierre (24/10/2026 23:59 UTC)

- [x] Borrado de datos (29/10/2026, Santiago): `data/`, `results/`, `notes/private/`, `ref/`,
  puntero de caché HF, logs del asistente de IA y filas del proyecto en claude-mem.
  El historial del repo nunca contuvo datos del dataset: no hizo falta reescribirlo.
- [x] Ian borró su copia y envió su confirmación a cnb@sagebase.org.
- El repo queda público para el jurado. Ganadores: 18/12/2026; los premios se liberan con
  las confirmaciones de borrado + documentación fiscal y screening.
