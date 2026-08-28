# Preguntas abiertas

> Nota: el fenotipo del proband (términos HPO + descripción clínica) sale del
> `Challenge_Clinical_Phenotype_1.docx`, que es de acceso controlado y dice
> "Do not redistribute". No se transcribe acá. Versión completa en
> `notes/private/` (gitignored). Resumen apto: el cluster fenotípico
> (predisposición a cáncer + restricción del crecimiento + anomalía renal +
> perinatal adverso + pérdida reproductiva parental) es compatible con
> **BUB1B / MVA1**.

## Para preguntar en el Community page del hackathon
- [ ] ¿Cómo se reparten 1er/2do/3er premio entre Track 1 y Track 2? Las reglas
      listan los montos pero no dicen si son por track o combinados.
- [ ] ¿Cómo se paga el premio en efectivo a participantes fuera de EEUU (Argentina)?
- [ ] ¿Una VM personal en la nube cuenta como "personal compute environment" a
      efectos de la obligación de borrado?

## Resueltas con los datos en mano (script 01) -- 2026-08-26

Hechos de formato/procedencia del VCF (no son genotipos individuales):

- [x] **11 archivos** = 1 doc clínico + VCF + `.tbi` + 8 FASTQ (R1/R2 × L001–L004,
      ~85 GB). **No hay BAM/CRAM.** La fase 2 arranca desde FASTQ: hay que alinear.
- [x] **1 sola muestra** en el VCF (`WGS_EX2312012`) — solo el proband, **no es
      trío**. La heterocigosis compuesta hay que fasearla sin padres (`PGT`/`PID`
      de GATK, o reads en fase 2).
- [x] **5.012.204 variantes.** Caller: **GATK HaplotypeCaller 4.2.4.0** +
      `VariantFiltration` (hard filters QD2/MQ40/RPRS-8/FS60/MQRankSum-12.5),
      corrido en DNAnexus. Ref: GRCh38 `no_alt` analysis set + hs38d1, contigs
      **sin** prefijo `chr`.
- [x] **No viene anotado.** INFO solo trae campos nativos de GATK (AC/AF/AN/DP/MQ/
      QD/FS/SOR/*RankSum/DB/ExcessHet/InbreedingCoeff/MLEAC/MLEAF). Hay que correr
      VEP / bcftools annotate para gnomAD/ClinVar/SpliceAI. `DB` = solo flag dbSNP.

## Abiertas para fase 1 (antes del envío #1)
- [ ] VEP completo (HGVS + transcripción) sobre las candidatas del gen priorizado.
- [ ] ClinVar / REVEL / AlphaMissense sobre la 2ª candidata: ¿es el 2º alelo real
      o el 2º sigue oculto (intrón profundo / MEI / SV)?
- [ ] SpliceAI / Pangolin sobre variantes intrónicas raras del gen priorizado.
- [ ] Exomiser / LIRICAL con los HPO del doc clínico.
- [ ] Envío #1 como sonda → leer el score del leaderboard.

## Bitácora
- 2026-08-26: acceso al dataset concedido. Estructura del proyecto armada.
- 2026-08-26: setup + triage inicial. Detalle en `notes/01-metodo-dia1.md`;
  versión con datos en `notes/private/`.
