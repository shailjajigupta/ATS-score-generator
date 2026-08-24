import React, { useState } from 'react'
import TextOrFileInput from './components/TextOrFileInput.jsx'
import ResultsPanel from './components/ResultsPanel.jsx'
import Loading from './components/Loading.jsx'
import ErrorAlert from './components/ErrorAlert.jsx'
import { analyzeCompatibility } from './services/api.js'

export default function App() {
  const [resume, setResume] = useState({ text: '', file: null })
  const [jd, setJd] = useState({ text: '', file: null })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const resumeProvided = resume.text.trim() || resume.file
  const jdProvided = jd.text.trim() || jd.file

  async function handleAnalyze(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await analyzeCompatibility({
        resumeText: resume.text,
        resumeFile: resume.file,
        jdText: jd.text,
        jdFile: jd.file,
      })
      setResult(data)
    } catch (err) {
      setError(err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setResult(null)
    setResume({ text: '', file: null })
    setJd({ text: '', file: null })
    setError('')
  }

  return (
    <div className="container" style={{ maxWidth: 900 }}>
      <div className="hero">
        <h1>
          Resume <span className="accent">×</span> JD Compatibility Analyzer
        </h1>
        <p>
          Paste or upload your resume and a job description. We'll score the match,
          compare skills, and suggest concrete improvements.
        </p>
      </div>

      <ErrorAlert message={error} onClose={() => setError('')} />

      {loading && <Loading text="Analyzing your resume against the job description... this can take up to 30 seconds the first time." />}

      {!loading && !result && (
        <form onSubmit={handleAnalyze} className="card p-4 mb-5">
          <div className="row">
            <div className="col-md-6 mb-4 mb-md-0">
              <TextOrFileInput
                label="Resume"
                placeholder="Paste your resume text here..."
                value={resume}
                onChange={setResume}
              />
            </div>
            <div className="col-md-6">
              <TextOrFileInput
                label="Job Description"
                placeholder="Paste the job description here..."
                value={jd}
                onChange={setJd}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100 mt-4"
            disabled={!resumeProvided || !jdProvided}
          >
            Analyze Compatibility
          </button>
        </form>
      )}

      {!loading && result && (
        <div className="card p-4 mb-5">
          <ResultsPanel result={result} onReset={handleReset} />
        </div>
      )}
    </div>
  )
}
