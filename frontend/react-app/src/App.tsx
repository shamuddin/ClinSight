import { useState } from 'react'
import AgentActivity from './components/AgentActivity'
import ImageViewer from './components/ImageViewer'
import FindingsPanel from './components/FindingsPanel'
import LabAlertsPanel from './components/LabAlertsPanel'
import SafetyPanel from './components/SafetyPanel'
import ReportViewer from './components/ReportViewer'
import AuditLog from './components/AuditLog'
import SafetyBanner from './components/SafetyBanner'
import PhysicianVeto from './components/PhysicianVeto'
import Dashboard from './components/Dashboard'

function App() {
  const [caseId, setCaseId] = useState('')
  const [result, setResult] = useState(null)

  return (
    <div className="app">
      <header><h1>ClinSight</h1></header>
      <SafetyBanner />
      <Dashboard onSelect={setCaseId} />
      <div className="panels">
        <ImageViewer caseId={caseId} />
        <AgentActivity />
        <FindingsPanel />
        <LabAlertsPanel />
        <SafetyPanel />
        <ReportViewer />
        <AuditLog />
        <PhysicianVeto />
      </div>
    </div>
  )
}

export default App
