# Plan y estado — Track 1

Versión publicable (estrategia y método). Sin genotipos ni coordenadas de
candidatas — eso vive en `notes/private/`.

## Dónde estamos (2026-08-26, fin del día 1 + anotación profunda)

- **Alelo #1: resuelto.** El pipeline identifica en BUB1B un alelo truncante que
  ClinVar clasifica **Pathogenic/Likely_pathogenic para "Mosaic variegated
  aneuploidy syndrome 1"** (múltiples submitters, sin conflictos), ultra-raro,
  LOFTEE HC, CADD 36. No es un candidato, es la respuesta para el 1er alelo.
- **Alelo #2: candidato fuerte, ~50–60 % de confianza.** Segundo alelo missense
  raro en BUB1B: **AlphaMissense 0.92 (likely_pathogenic)**, ausente de gnomAD,
  en el último exón (proteína alterada, compatible con hipomórfico). Contras: el
  cambio de aminoácido figura en ClinVar como **VUS** (single submitter) y falta
  confirmar la **fase** (cis/trans respecto del truncante; están a ~11 kb, GATK
  no los faseó). Puede ser el 2º alelo real o un pasajero con el verdadero 2º hit
  críptico (intrón profundo / MEI / SV) → fase 2.
- **Fase 2 (reads): sin empezar.** Bajar 85 GB + alinear + phasing con reads +
  SpliceAI/Pangolin + MELT sobre BUB1B.
- **Fenotipo: confirmado (proxy liviano).** Phen2Gene rankea BUB1B #1 del panel
  y top 0.2 % genoma-wide con los HPO del caso. Exomiser/LIRICAL "de verdad"
  pendiente (necesita Java + ~20 GB de datos hg38; no instalado).
- `epcr` (fase 3) sin calibrar.

**Lectura honesta:** mejor que ayer. Probablemente tenemos **los dos alelos** ya
desde el VCF — el #1 seguro, el #2 defendible. Piso realista subió: el envío #1
deja de ser una apuesta a medias. Techo (podio): sigue dependiendo de que el #2
sea correcto (o de encontrar el críptico si no lo es) y de un `epcr` bien
calibrado. ~30–35 % del camino. Runway: ~7–8 fines de semana, 6 envíos.

## Próximos pasos por ROI

1. ~~ClinVar + AlphaMissense sobre las candidatas BUB1B~~ **HECHO (2026-08-26).**
   Alelo #1 = truncante ClinVar P/LP para MVA1. Alelo #2 = missense AlphaMissense
   0.92, gnomAD-ausente, pero VUS en ClinVar y fase sin confirmar.
2. ~~Priorización por fenotipo~~ **HECHO (proxy Phen2Gene).** BUB1B #1 del panel.
   Pendiente: Exomiser/LIRICAL real (Java + datos hg38) para scoring de variante
   + ACMG — setup aparte, ~20 GB.
3. **Envío #1 como sonda** con el par BUB1B como `primary` (`epcr` ~0,92 / ~0,5).
   El leaderboard dice si el 2º alelo es correcto (2 alelos) o si falta (1 alelo).
   **Siguiente acción concreta.**
4. **Según (3):** si falta el 2º → fase 2 (bajar FASTQ, alinear, phasing con
   reads, SpliceAI/Pangolin en intrones de BUB1B, MELT en BUB1B). Si están los
   dos → calibrar `epcr`, sumar 2–3 hallazgos secundarios bien razonados,
   fase 4 (Snakemake/Nextflow + writeup).
5. Confirmar **fase** de las dos BUB1B: intentar phasing con reads (aunque estén
   a 11 kb, algún par o read solapando ayuda), o dejarlo para long-read/fase 2.

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
