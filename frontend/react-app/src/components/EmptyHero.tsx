import type { CSSProperties } from 'react'

export default function EmptyHero({ onRunDemo }: { onRunDemo: () => void }) {
  return (
    <div className="empty-hero empty-hero--architecture">
      <div className="empty-hero-content">
        {/* Abstract generative curves */}
        <svg
          viewBox="0 0 600 180"
          fill="none"
          style={{ width: '100%', maxWidth: 560, marginBottom: 32 }}
          aria-hidden="true"
        >
          <path
            d="M10 140 Q 80 20, 150 90 T 300 60 T 450 100 T 590 40"
            stroke="#e5e5e5"
            strokeWidth="1"
            fill="none"
          />
          <path
            d="M10 140 Q 80 20, 150 90 T 300 60 T 450 100 T 590 40"
            stroke="#171717"
            strokeWidth="1.5"
            fill="none"
            strokeDasharray="800"
            strokeDashoffset="800"
            style={{ animation: 'line-draw 3s ease forwards' } as CSSProperties}
          />
          <path
            d="M10 100 Q 100 160, 200 80 T 350 120 T 500 50 T 590 90"
            stroke="#e5e5e5"
            strokeWidth="1"
            fill="none"
          />
          <path
            d="M10 100 Q 100 160, 200 80 T 350 120 T 500 50 T 590 90"
            stroke="#171717"
            strokeWidth="1"
            fill="none"
            strokeDasharray="800"
            strokeDashoffset="800"
            style={{ animation: 'line-draw 3s 0.6s ease forwards' } as CSSProperties}
          />
          <path
            d="M10 60 Q 120 10, 220 70 T 380 30 T 540 110 T 590 70"
            stroke="#e5e5e5"
            strokeWidth="0.5"
            fill="none"
          />
          <path
            d="M10 60 Q 120 10, 220 70 T 380 30 T 540 110 T 590 70"
            stroke="#a3a3a3"
            strokeWidth="0.5"
            fill="none"
            strokeDasharray="800"
            strokeDashoffset="800"
            style={{ animation: 'line-draw 3s 1.2s ease forwards' } as CSSProperties}
          />
          {/* Nodes at intersections */}
          <circle cx="150" cy="90" r="4" fill="#fff" stroke="#171717" strokeWidth="1.5" />
          <circle cx="300" cy="60" r="4" fill="#fff" stroke="#171717" strokeWidth="1.5" />
          <circle cx="450" cy="100" r="4" fill="#fff" stroke="#171717" strokeWidth="1.5" />
        </svg>

        <h1 className="empty-hero-title">Multi-Agent Clinical Decision Support</h1>
        <p className="empty-hero-sub">12 reasoning agents, 4 safety guards, AMD MI300X ready</p>

        <div className="empty-hero-actions">
          <button type="button" className="primary-demo-btn" onClick={onRunDemo}>
            Run Grand Demo
          </button>
          <span className="empty-hero-hint dim">or press 1-6 to load a case</span>
        </div>
      </div>
    </div>
  )
}
