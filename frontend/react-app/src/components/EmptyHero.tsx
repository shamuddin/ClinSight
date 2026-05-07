import { Activity, Play } from 'lucide-react'

export default function EmptyHero({ onRunDemo }: { onRunDemo: () => void }) {
  return (
    <div className="empty-hero">
      <div className="empty-hero-content">
        {/* Soft gradient orb */}
        <div
          style={{
            width: 120,
            height: 120,
            borderRadius: '50%',
            background: 'radial-gradient(circle at 30% 30%, rgba(13,148,136,0.15), rgba(13,148,136,0.04))',
            margin: '0 auto 28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Activity size={40} color="#0d9488" strokeWidth={1.5} />
        </div>

        <h1 className="empty-hero-title">ClinSight</h1>
        <p className="empty-hero-sub">
          Multi-agent clinical decision support for chest X-ray analysis
        </p>

        <div className="empty-hero-agents">
          <div className="empty-agent-chip">
            <span className="empty-agent-num">5</span>
            Parent Agents
          </div>
          <div className="empty-agent-chip">
            <span className="empty-agent-num">7</span>
            Subagents
          </div>
          <div className="empty-agent-chip">
            <span className="empty-agent-num">4</span>
            Safety Guards
          </div>
        </div>

        <div className="empty-hero-actions">
          <button type="button" className="primary-demo-btn" onClick={onRunDemo}>
            <Play size={14} />
            Run Grand Demo
          </button>
          <span className="empty-hero-hint dim">or press 1–6 to load a case</span>
        </div>
      </div>
    </div>
  )
}
