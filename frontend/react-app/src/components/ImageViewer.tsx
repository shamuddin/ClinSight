import { CaseResult } from '../types'

export default function ImageViewer({ result }: { result: CaseResult }) {
  // Generate a deterministic SVG placeholder based on case ID
  const seed = result.case_id.split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  const hues = [200, 160, 320, 40, 280, 120]
  const hue = hues[seed % hues.length]

  return (
    <div className="panel">
      <h2>Image Viewer</h2>
      <div className="image-container">
        <svg viewBox="0 0 512 512" className="xray-svg">
          <rect width="512" height="512" fill="#0b1220" />
          <ellipse cx="256" cy="200" rx="90" ry="110" fill={`hsl(${hue},20%,18%)`} stroke={`hsl(${hue},40%,35%)`} strokeWidth="2" />
          <ellipse cx="256" cy="200" rx="70" ry="90" fill={`hsl(${hue},15%,14%)`} />
          <rect x="200" y="290" width="112" height="140" rx="20" fill={`hsl(${hue},20%,16%)`} stroke={`hsl(${hue},40%,30%)`} strokeWidth="2" />
          <line x1="256" y1="90" x2="256" y2="310" stroke={`hsl(${hue},40%,25%)`} strokeWidth="2" />
          <line x1="166" y1="200" x2="346" y2="200" stroke={`hsl(${hue},40%,25%)`} strokeWidth="2" />
          {/* Attention region overlays */}
          {result.attention_regions.map((r) => (
            <rect
              key={r.finding_id}
              x={r.x}
              y={r.y}
              width={r.w}
              height={r.h}
              fill="none"
              stroke="#f59e0b"
              strokeWidth="2"
              strokeDasharray="4 2"
            />
          ))}
        </svg>
        <div className="image-meta">
          <div>{result.case_id}</div>
          <div className="dim">Modality: CXR (PA) — Demo placeholder</div>
          <div className="dim">{result.findings.length} findings · {result.attention_regions.length} attention regions</div>
        </div>
      </div>
    </div>
  )
}
