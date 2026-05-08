# AMD Hardware Proof — Step-by-Step Guide
## How to Capture Live rocm-smi Evidence During Inference

This guide produces three pieces of evidence that satisfy the Grand Prize tier:
1.  **Live terminal recording** — type `rocm-smi` while inference is running.
2.  **Screenshots** — still images of GPU utilization spiking.
3.  **Video clip** — short screen recording (30–60s) for demo reel.

---

## OPTION A: SSH into Droplet (Recommended — Most Convincing)

### Prerequisites
- You have added the SSH key to `/root/.ssh/authorized_keys` on the droplet.
- The droplet is running (we confirmed it is).

### Step 1 — Open 3 terminal windows

| Window | Purpose |
|--------|---------|
| **Window A** | SSH into droplet, run `watch -n 1 rocm-smi` |
| **Window B** | SSH into droplet, trigger inference with `curl` |
| **Window C** | (Optional) Local screen recorder (OBS, Loom, or phone camera pointed at screen) |

### Step 2 — Window A: Start live rocm-smi monitoring

```bash
ssh -o ConnectTimeout=10 -i /root/.ssh/authorized_keys root@129.212.176.125 "watch -n 1 'rocm-smi --showproductname --showmeminfo vram'"
```

What you will see:
```
Device  Node  IDs              Temp        Power     Partitions          SCLK     MCLK    Fan  Perf  PwrCap  VRAM%  GPU%
0       1     0x74b5,   21947  38.0°C      197.0W    NPS1, SPX, 0        2109Mhz  900Mhz  0%   auto  750.0W  88%    0%
```

**Key fields judges look for:**
- `Device` = `0x74b5` (AMD MI300X DID)
- `Temp` = ~38–45°C
- `Power` = ~195–280W (varies with load)
- `VRAM%` = ~85–92% (both models loaded)
- `GPU%` = 0% (idle right now)

### Step 3 — Window B: Trigger live inference

```bash
ssh -o ConnectTimeout=10 -i /root/.ssh/authorized_keys root@129.212.176.125 "curl -s --connect-timeout 5 -m 90 http://localhost:3000/demo/analyze/CS-2024-001 | grep -E 'esi_level|total_time_ms|mode|inference_time_sec'"
```

This will take **~60 seconds** (the real inference time).

### Step 4 — Capture the spike

While Window B is running, **watch Window A**. You will see:

**Before inference** (0s):
```
GPU% = 0%   |   Power = 197W   |   Temp = 38°C
```

**During inference** (~10–60s):
```
GPU% = 85–100%   |   Power = 280–300W   |   Temp = 42–48°C
```

**After inference** (~65s):
```
GPU% = 0%   |   Power = 198W   |   Temp = 39°C
```

### Step 5 — Save evidence

**Screenshot method (fastest):**
1. When GPU% spikes to 85%+, take a screenshot of Window A.
2. Save as `benchmarks/rocm_smi_during_live.png`.
3. Also screenshot Window B showing the JSON result with `"mode": "LIVE"` and `"inference_time_sec": 67.8`.
4. Save as `benchmarks/inference_result_live.png`.

**Terminal text dump (for repo):**
```bash
# On droplet, run this AFTER inference completes:
ssh -o ConnectTimeout=10 -i /root/.ssh/authorized_keys root@129.212.176.125 "rocm-smi --showmeminfo vram --showproductname --showserial" > benchmarks/rocm_smi_full_evidence.txt
```

This produces a text file with:
- Exact GPU model name (`AMD MI300X`)
- Serial number (if available)
- VRAM allocation details

---

## OPTION B: Record a Video Clip (Best for Demo Reel)

### Method 1: OBS Studio (Free, Cross-Platform)

**Setup:**
1. Download OBS Studio from `obsproject.com`.
2. Create a **Scene** with two **Sources**:
   - **Source 1:** Terminal window (Window Capture) — shows `watch -n 1 rocm-smi`
   - **Source 2:** Browser window (Window Capture) — shows `http://129.212.176.125:3000`
3. Arrange side-by-side (split screen). Terminal on left, browser on right.

**Recording sequence (60 seconds total):**
1. **0–5s:** Show terminal with idle rocm-smi (GPU% = 0%).
2. **5–10s:** Click "Analyze" in browser on Case 001.
3. **10–15s:** Narration: *"Triggering live inference on AMD MI300X..."*
4. **15–55s:** Show terminal GPU% climbing to 85%+, power climbing to 280W.
   - Add on-screen text overlay: `GPU utilization spike = real inference`
5. **55–60s:** Browser shows results. Point to `"mode": "LIVE"` and `67.8s` latency.

**Export settings:**
- Resolution: 1920x1080
- Format: MP4 (H.264)
- File: `docs/demo_amd_hardware_proof.mp4`
- Target size: under 20MB

### Method 2: Terminal Recorder (Asciinema — Lightweight, Text-Based)

```bash
# Install on your local machine
brew install asciinema   # macOS
apt install asciinema    # Ubuntu

# Record a terminal session showing the full flow
asciinema rec demo_amd_hardware.cast

# Inside the recording:
#   1. ssh into droplet
#   2. rocm-smi
#   3. curl /demo/analyze/CS-2024-001
#   4. rocm-smi again while waiting
#   5. Show result JSON
# Press Ctrl+D to stop

# Upload (optional — generates shareable URL)
asciinema upload demo_amd_hardware.cast
```

**Pros:**
- No video file — just a text-based replay.
- Judges can copy/paste exact output.
- Lightweight (< 100 KB).

**Cons:**
- No browser window visible.
- Less visually impressive than split-screen video.

### Method 3: Phone Camera (Emergency Backup)

If OBS fails or SSH is unstable:
1. Open two browser tabs on your laptop:
   - Tab 1: `http://129.212.176.125:3000` (live demo)
   - Tab 2: Terminal via DigitalOcean console (rocm-smi)
2. Position phone camera to capture both screens side-by-side.
3. Hit "Analyze" on Case 001.
4. Record for 90 seconds (covers full inference).
5. Transfer MP4 to laptop, trim to 45 seconds.

**This is acceptable for hackathon proof.** Judges do not expect Hollywood production. They want to see the GPU utilization spike in the same frame as the inference request.

---

## OPTION C: Automated Script (Capture Without Manual Screenshots)

If you want to automate the entire evidence capture, run this on the droplet via SSH:

```bash
#!/bin/bash
# /workspace/scripts/capture_amd_evidence.sh
# Run this ON the droplet

OUTDIR=/mnt/scratch/clinsight-clean/benchmarks/gpu_results/$(date +%Y%m%d_%H%M%S)
mkdir -p $OUTDIR

# 1. Baseline rocm-smi
echo "=== BASELINE ===" > $OUTDIR/evidence.txt
rocm-smi --showproductname --showmeminfo vram >> $OUTDIR/evidence.txt 2>&1

# 2. Start inference in background, capture its PID
curl -s --connect-timeout 5 -m 120 http://localhost:3000/demo/analyze/CS-2024-001 > $OUTDIR/result.json &
CURL_PID=$!

# 3. Capture rocm-smi every 2 seconds during inference
for i in $(seq 1 40); do
    echo "=== SAMPLE $i ===" >> $OUTDIR/evidence.txt
    rocm-smi --showmeminfo vram >> $OUTDIR/evidence.txt 2>&1
    sleep 2
done

# 4. Wait for inference to finish
wait $CURL_PID

# 5. Post-inference rocm-smi
echo "=== POST ===" >> $OUTDIR/evidence.txt
rocm-smi --showproductname --showmeminfo vram >> $OUTDIR/evidence.txt 2>&1

echo "Evidence saved to $OUTDIR"
```

Run it:
```bash
ssh -o ConnectTimeout=10 -i /root/.ssh/authorized_keys root@129.212.176.125 "bash -s" < /workspace/scripts/capture_amd_evidence.sh
```

This produces:
- `evidence.txt` — 40 samples of rocm-smi across the full inference window.
- `result.json` — the actual live inference output with `"mode": "LIFE"`.

A judge can read `evidence.txt` and see GPU utilization climb from 0% to 85%+ and back to 0% — exactly matching the inference duration.

---

## WHAT THE FINAL EVIDENCE PACKAGE LOOKS LIKE

Grand Prize tier projects present hardware proof like this:

```
benchmarks/
├── real_benchmark.json                              ← 6-case JSON (exists)
├── latency_histogram_real.png                       ← histogram (exists)
├── rocm_smi_baseline.txt                            ← text dump (exists)
├── rocm_smi_during.txt                              ← text dump (exists)
├── rocm_smi_post_e2e.txt                            ← text dump (exists)
├── rocm_smi_during_live.png     ← NEW: screenshot of GPU% spike
├── inference_result_live.png    ← NEW: screenshot of JSON result
├── demo_amd_hardware_proof.mp4  ← NEW: 45s split-screen video
└── 20260508_143000/               ← NEW: automated capture dir
    ├── evidence.txt
    └── result.json
```

---

## JUDGE VERDICTION SCALE

| Evidence Level | What Judge Sees | Verdict |
|---------------|-----------------|---------|
| **Aspirational** | `README says "AMD MI300X"` | Unverified claim. 4/10. |
| **Competitive** | `rocm-smi` text file + static screenshot | Credible. 7/10. |
| **Grand Prize** | Live terminal recording showing GPU% spike during inference, split-screen with browser result, video clip in repo | **"This is real." 10/10.** |

---

## COMMON MISTAKES TO AVOID

1. **Don't run rocm-smi ONCE before and ONCE after.** Judges want to see the DURING state. Capture at least 10 samples during the ~60s inference window.

2. **Don't screenshot only the browser.** The browser showing a result does not prove it ran on AMD. The terminal showing `GPU% = 95%` at the same timestamp proves it.

3. **Don't use cached results for the video.** If the backend serves `"cached": true`, the GPU% stays at 0%. Make sure `/health` returns `"cached": false` before recording.

4. **Don't forget the product name.** `rocm-smi` must show `MI300X` or the judge cannot verify the GPU model. Use `rocm-smi --showproductname`.

---

*Guide generated: May 8, 2026*
