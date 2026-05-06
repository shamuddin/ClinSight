import { Cpu, ExternalLink, GitBranch, Server, ShieldCheck, X } from 'lucide-react'

export default function AboutModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="about-modal-title">
      <div className="modal-card modal-card--wide">
        <div className="modal-header">
          <div>
            <span className="evidence-kicker">Architecture + Hardware</span>
            <h3 id="about-modal-title">ClinSight System</h3>
          </div>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close architecture modal">
            <X size={16} />
          </button>
        </div>

        <div className="about-grid">
          <section className="about-panel">
            <div className="about-panel-title">
              <GitBranch size={15} />
              Agent Graph
            </div>
            <div className="architecture-flow">
              {['Coordinator', 'Radiologist', 'Lab Analyst', 'Safety', 'Documenter'].map((node, index) => (
                <div key={node} className="architecture-node">
                  <span>{index + 1}</span>
                  <strong>{node}</strong>
                </div>
              ))}
            </div>
            <p>
              Five parent agents coordinate twelve reasoning nodes: image quality, pediatric safety,
              pathology analysis, critical labs, pattern correlation, contradiction checks,
              hallucination guard, bias audit, safety merge, ESI scoring, differential, and reporting.
            </p>
          </section>

          <section className="about-panel">
            <div className="about-panel-title">
              <Cpu size={15} />
              AMD MI300X Surface
            </div>
            <div className="hardware-stats">
              <div><span>VRAM</span><strong>192 GB HBM3</strong></div>
              <div><span>Vision</span><strong>Qwen2.5-VL-7B</strong></div>
              <div><span>Text</span><strong>Qwen3.5-35B-A3B</strong></div>
              <div><span>Loaded</span><strong>~84-99 GB</strong></div>
            </div>
          </section>

          <section className="about-panel">
            <div className="about-panel-title">
              <ShieldCheck size={15} />
              Safety Layer
            </div>
            <ul className="about-list">
              <li>14 deterministic emergency lab thresholds</li>
              <li>Contradiction checks across image, labs, and triage note</li>
              <li>Hallucination guard for grounding and anatomical scope</li>
              <li>Bias auditor with confidence penalties and physician veto</li>
            </ul>
          </section>

          <section className="about-panel">
            <div className="about-panel-title">
              <Server size={15} />
              Verifiable Artifacts
            </div>
            <div className="about-links">
              <a href="/docs/architecture.md" target="_blank" rel="noreferrer">
                Architecture docs <ExternalLink size={12} />
              </a>
              <a href="/docs/amd_setup.md" target="_blank" rel="noreferrer">
                AMD setup <ExternalLink size={12} />
              </a>
              <a href="/docs/benchmark_results.md" target="_blank" rel="noreferrer">
                Benchmarks <ExternalLink size={12} />
              </a>
              <a href="/docs/pitch_deck.html" target="_blank" rel="noreferrer">
                Pitch deck <ExternalLink size={12} />
              </a>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
