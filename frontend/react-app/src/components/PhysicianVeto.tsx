export default function PhysicianVeto({ onVeto }: { onVeto: (action: string) => void }) {
  return (
    <div className="panel">
      <h2>Physician Override</h2>
      <div className="veto-buttons">
        <button className="btn btn-success" onClick={() => onVeto('agreed')}>Agree</button>
        <button className="btn btn-warning" onClick={() => onVeto('overridden')}>Override</button>
        <button className="btn btn-danger" onClick={() => onVeto('dismissed')}>Dismiss</button>
      </div>
    </div>
  )
}
