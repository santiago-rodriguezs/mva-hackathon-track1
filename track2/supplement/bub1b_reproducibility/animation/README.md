# BUB1B animation — enhanced Gemini version

Extract the ZIP completely. Open PowerShell in the folder containing both `animate.py` and `requirements.txt`.

```powershell
python -m pip install -r requirements.txt
python animate.py --quality preview
python animate.py --quality final
```

The final output is `renders/BUB1B_explainer.mp4`: 180 seconds, 1920×1080, 60 fps. No audio is included. English subtitles are embedded; `captions.srt` and `NARRATION.md` are also supplied.

For a short test:

```powershell
python animate.py --quality preview --start 40 --end 48 --output renders/test.mp4
python animate.py --stills
```

Preserves the Gemini Cairo/Pillow drawing architecture, Latin Modern fonts and original C-alpha structure data. The fallback renderer forces 4× supersampling. Installing `pycairo` enables native vector antialiasing; `cairocffi` is also detected when a system Cairo library is available. Cairo is optional on Windows.

The more decisive treatment narrative proposes 4-PBA for experimental evaluation. Folding rescue is a hypothesis, not an observed response. NMN, TUDCA and amlexanox are separate mechanistic alternatives. The MCC branch inhibits APC/C. Structure values refer to the wild-type AlphaFold model; the embedded polar-contact coordinates are taken from AF-O60566-F1-model_v6. Distances are atomic, not C-alpha distances. Depth is rendered by painter-sorted segments, not a per-pixel Z-buffer.

CLI options remain compatible, including width, fps, supersample, start/end, output, preset, crf and stills. Fonts and structural JSON must remain beside the script in `assets/`.


## Relationship to the scientific results

The coordinates represent a WT structural model; interpolated folding/unfolding is explanatory animation, not molecular dynamics. Predicted rescue, drug waves and clean segregation are illustrations of hypotheses, not experimental observations. The report's conditional mechanism and unknown phase take precedence over the simplified visual story. The final comparative measurements are in `../analysis/results/`.

The 180-second source includes no audio. Full-length MP4 renders are intentionally not stored in this support directory; reproduce them from this code. The code, fonts, structure data and subtitles are included.
