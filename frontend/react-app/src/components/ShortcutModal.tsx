import { Keyboard, X } from 'lucide-react'

const SHORTCUTS = [
  ['1-6', 'Load demo case'],
  ['A', 'Physician agree'],
  ['O', 'Physician override'],
  ['D', 'Physician dismiss'],
  ['R', 'Rerun current case'],
  ['?', 'Show shortcuts'],
  ['Esc', 'Close modal or stop stream'],
]

export default function ShortcutModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="shortcut-modal-title">
      <div className="modal-card modal-card--small">
        <div className="modal-header">
          <div>
            <span className="evidence-kicker">Keyboard Layer</span>
            <h3 id="shortcut-modal-title">
              <Keyboard size={16} />
              Shortcuts
            </h3>
          </div>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close shortcuts modal">
            <X size={16} />
          </button>
        </div>
        <div className="shortcut-list">
          {SHORTCUTS.map(([key, action]) => (
            <div key={key} className="shortcut-row">
              <kbd>{key}</kbd>
              <span>{action}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
