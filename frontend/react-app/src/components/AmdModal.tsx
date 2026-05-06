import { Cpu, Gauge, HardDrive, Server, X } from 'lucide-react'

export default function AmdModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="amd-modal-title">
      <div className="modal-card modal-card--wide">
        <div className="modal-header">
          <div>
            <span className="evidence-kicker">AMD Performance Surface</span>
            <h3 id="amd-modal-title">
              <Cpu size={17} />
              MI300X Hardware Profile
            </h3>
          </div>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close AMD modal">
            <X size={16} />
          </button>
        </div>

        <div className="amd-modal-grid">
          <section className="amd-hero-stat">
            <HardDrive size={18} />
            <span>VRAM</span>
            <strong>192 GB HBM3</strong>
            <p>Enough headroom for the vision model, text model, and concurrent clinical requests on one accelerator.</p>
          </section>

          <section className="amd-stack-panel">
            <div className="about-panel-title">
              <Server size={15} />
              Model Stack
            </div>
            <div className="hardware-stats">
              <div><span>Vision VLM</span><strong>Qwen2.5-VL-7B</strong></div>
              <div><span>Text LLM</span><strong>Qwen3.5-35B-A3B</strong></div>
              <div><span>Runtime</span><strong>vLLM + ROCm</strong></div>
              <div><span>Footprint</span><strong>~84-99 GB</strong></div>
            </div>
          </section>

          <section className="amd-stack-panel">
            <div className="about-panel-title">
              <Gauge size={15} />
              Demo Benchmark Artifacts
            </div>
            <div className="amd-benchmark-row">
              <span>Mock P50</span>
              <strong>13 ms</strong>
            </div>
            <div className="amd-benchmark-row">
              <span>Mock P95</span>
              <strong>18.4 ms</strong>
            </div>
            <div className="amd-benchmark-row">
              <span>Success</span>
              <strong>100%</strong>
            </div>
            <p className="amd-note">Real MI300X proof belongs in the benchmark artifacts and video path when available.</p>
          </section>
        </div>
      </div>
    </div>
  )
}
