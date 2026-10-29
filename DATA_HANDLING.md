# Obligaciones sobre los datos

El dataset `SageBio/mva-hackathon-2026-data` es el genoma completo de un chico
vivo. El acceso se concede individualmente y bajo terminos que aceptaste el
26/08/2026. No son formalidades: incumplirlos es causal de descalificacion.

## Reglas duras

1. **Nunca commitear datos.** Ni FASTQ, ni BAM, ni VCF, ni ninguna tabla que
   contenga genotipos individuales. El `.gitignore` bloquea las extensiones
   habituales, pero igual mirar `git status` antes de cada commit.
2. **No compartir, ni dentro del equipo.** Cada integrante se registra en
   Hugging Face, acepta los terminos y baja su propia copia. Sin bucket
   compartido, sin Drive, sin scp entre nosotros.
3. **Un solo entorno.** Los datos viven aca (esta Mac) y, si hace falta para la
   fase 2, en UNA VM personal de acceso restringido. Cada entorno extra es un
   entorno mas que hay que borrar y certificar.
4. **No intentar reidentificar ni contactar** al chico, su familia, ni a nadie
   de la MVA Society.
5. **Embargo de publicacion** hasta que los organizadores publiquen su resumen.

## Checklist de borrado (dentro de los 30 dias del 24/10/2026)

- [ ] Borrar `data/` y `ref/` en esta maquina
- [ ] Borrar discos, snapshots y storage de cualquier VM usada
- [ ] Borrar el cache de Hugging Face (`~/.cache/huggingface/`)
- [ ] Vaciar la papelera
- [ ] Borrar logs propios con bloques de variantes (transcripts del asistente de IA,
      memoria local tipo claude-mem)
- [ ] Cada integrante manda mail a **cnb@sagebase.org** confirmando (direccion indicada
      por los organizadores el 28/10/2026; plazo 23/11/2026)

## Que SI se puede publicar

El codigo, el pipeline, el writeup de metodos, figuras agregadas que no expongan
genotipos individuales, y el CSV final de candidatos (que es la submission misma).
