import React, { useRef, useState } from 'react'

/**
 * A labeled input block that lets the user either paste text or upload a
 * file (.pdf, .docx, .txt). Reports back up via onChange with
 * { text, file } - exactly one of which will be populated.
 */
export default function TextOrFileInput({ label, placeholder, value, onChange }) {
  const [mode, setMode] = useState('paste') // 'paste' | 'upload'
  const [dragging, setDragging] = useState(false)
  const fileInputRef = useRef(null)

  function handleTextChange(e) {
    onChange({ text: e.target.value, file: null })
  }

  function handleFileSelected(file) {
    if (!file) return
    onChange({ text: '', file })
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    handleFileSelected(file)
  }

  function switchMode(newMode) {
    setMode(newMode)
    onChange({ text: '', file: null }) // reset when switching modes
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-2">
        <label className="form-label mb-0">{label}</label>
        <div className="input-mode-toggle">
          <button type="button" className={mode === 'paste' ? 'active' : ''} onClick={() => switchMode('paste')}>
            Paste text
          </button>
          <button type="button" className={mode === 'upload' ? 'active' : ''} onClick={() => switchMode('upload')}>
            Upload file
          </button>
        </div>
      </div>

      {mode === 'paste' ? (
        <textarea
          className="form-control"
          placeholder={placeholder}
          value={value.text}
          onChange={handleTextChange}
        />
      ) : (
        <div
          className={`dropzone ${dragging ? 'dragging' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => handleFileSelected(e.target.files?.[0])}
          />
          {value.file ? (
            <>
              <div>📄 File selected</div>
              <div className="dz-filename">{value.file.name}</div>
              <div className="small mt-1">Click to choose a different file</div>
            </>
          ) : (
            <>
              <div>Click to browse or drag a file here</div>
              <div className="small mt-1">.pdf, .docx, or .txt</div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
