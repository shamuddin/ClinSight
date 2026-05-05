import { CaseResult } from '../types'

export default function ReportViewer({ result }: { result: CaseResult }) {
  return (
    <div className="panel">
      <h2>Clinical Report</h2>
      <div className="report-section">
        <h3>Differential Diagnosis</h3>
        <ol className="numbered-list">
          {result.differential.map((d, i) => (
            <li key={i}>{d}</li>
          ))}
        </ol>
      </div>
      <div className="report-section">
        <h3>Suggested Actions</h3>
        <ul className="action-list">
          {result.suggested_actions.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ul>
      </div>
      <div className="report-section">
        <h3>Patient Context</h3>
        <p className="dim">
          {result.patient_age}yo {result.patient_sex}, {result.patient_race}
          <br />
          Chief complaint: {result.chief_complaint}
          <br />
          Vitals: BP {result.vitals.bp}, HR {result.vitals.hr}, RR {result.vitals.rr}, SpO₂{' '}
          {result.vitals.spo2}%, Temp {result.vitals.temp}°C
        </p>
      </div>
      <details>
        <summary>Raw report JSON</summary>
        <pre className="json-raw">{JSON.stringify(result.report, null, 2)}</pre>
      </details>
    </div>
  )
}
