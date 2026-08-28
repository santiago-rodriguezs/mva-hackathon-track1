# notes/

Bitácora y planificación del proyecto.

## Público vs privado

Este repo está pensado para ser público (ver `DATA_HANDLING.md`). Por eso:

- **`notes/*.md`** (este directorio, nivel raíz) — **publicable**. Método,
  decisiones de pipeline, cambios a los scripts, plan de trabajo, conclusiones a
  nivel gen. Nada de genotipos individuales, coordenadas de variantes del
  proband, profundidades de lectura, ni texto del documento clínico.

- **`notes/private/`** — **GITIGNORED, nunca se commitea**. Versión completa de
  cada nota con el detalle sensible: genotipos (`0/1`, `1/1`), `AD`/`DP`/`GQ`,
  coordenadas exactas de candidatas, y el fenotipo textual extraído del
  `Challenge_Clinical_Phenotype_1.docx` (que dice "Do not redistribute").

`.gitignore` bloquea `notes/private/`, `*_full.md` y `*.local.md`.
Igual: **`git status` antes de cada commit** (regla dura de `DATA_HANDLING.md`).

## Para un integrante nuevo del equipo

No se comparten datos, ni entre nosotros. Pedí tu propio acceso al dataset en
Hugging Face, aceptá los términos y bajá tu propia copia. Se colabora por este
repo (código), no por archivos de datos.
