# MVA Hackathon 2026 — Track 1

Pipeline de priorizacion de variantes para el caso de Mosaic Variegated
Aneuploidy del hackathon de Sage Bionetworks / Hugging Face / MVA Society.

- Space: https://huggingface.co/spaces/SageBio/rare-disease-real-kid-mva-hackathon-2026
- Cierre de envios: **24 de octubre de 2026** (deadline real nuestro: **18 de octubre**)
- Envios disponibles: **6**

> **Antes de tocar nada, leer [DATA_HANDLING.md](DATA_HANDLING.md).**
> Este repo va a ser publico; los datos no. Nunca se commitea un archivo
> derivado del genoma del proband.

## La estrategia en un parrafo

La enfermedad ya tiene diagnostico confirmado, asi que identificar el gen no es
el desafio: la respuesta esta casi seguro dentro del panel de
`config/mva_genes.tsv`. Es recesiva, o sea que la respuesta son **dos** variantes
en el mismo gen. La primera es facil y la va a encontrar todo el mundo filtrando
el VCF. La segunda es donde se define la competencia: en los casos publicados de
BUB1B, el segundo alelo suele estar escondido donde el VCF estandar no mira
(intron profundo, insercion de elemento movil, variante estructural), y por eso
el hackathon entrega los FASTQ crudos y no solo el VCF.

## Fases

| Fase | Que | Cuando | Rinde |
|---|---|---|---|
| 1 | Filtrado del VCF sobre el panel + priorizacion por fenotipo (Exomiser/LIRICAL) | FdS 1 | el primer alelo, ~50 pts |
| 2 | Vuelta a los reads: SV, elementos moviles (MELT/xTea), splicing intronico (SpliceAI/Pangolin) | FdS 2-5 | el segundo alelo |
| 3 | Calibracion de `epcr` para F-max + hallazgos secundarios | FdS 6 | |
| 4 | Repo reproducible (Snakemake/Nextflow) + writeup de metodos | FdS 7-8 | |

El **envio #1 es una sonda**: el leaderboard devuelve el score en vivo, y ese
numero te dice cuantos de los dos alelos tenes. Vale mas que un fin de semana de
analisis a ciegas.

## Uso

```bash
./scripts/setup_env.sh                  # dependencias (una vez)
./scripts/00_download_vcf.sh            # solo el VCF, no los 85 GB
python3 scripts/make_panel_bed.py       # coordenadas GRCh38 del panel
./scripts/01_inspect_vcf.sh data/WGS_EX2312012_HGWCNDSX7.vcf.gz
./scripts/02_panel_triage.sh data/WGS_EX2312012_HGWCNDSX7.vcf.gz
```

## Formato de entrega (Track 1)

CSV, hasta 10 filas, coordenadas GRCh38:

```
proband_id, chrom_1, pos_1, ref_1, alt_1, chrom_2, pos_2, ref_2, alt_2, epcr, finding_type, notes
```

- `chrom_2..alt_2` para el par en heterocigosis compuesta (vacio si no aplica)
- `epcr` en (0,1]: probabilidad estimada de causalidad. **Puntua F-max**, asi que
  no se rellenan las 10 filas salvo que cada una se la gane
- `finding_type`: `primary` o `secondary`. Los secundarios **no bajan** el score
  automatico, asi que conviene sumar dos o tres bien razonados
- Nombre del archivo: `santiago-rodriguezs_<metodo>.csv`

## Estructura

```
config/    panel de genes y BED derivado
scripts/   pipeline, numerados por orden de ejecucion
notes/     preguntas abiertas y bitacora
data/      datos del hackathon (GITIGNORED, se borra al final)
ref/       genoma de referencia (GITIGNORED)
results/   salidas intermedias (GITIGNORED)
```
