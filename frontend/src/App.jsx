import { useState } from 'react'
import './App.css'

function App() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [context, setContext] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  // Handle file selection
  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file)
      setError(null)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    } else {
      setError({ message: 'Please select a valid image file (JPEG, PNG, WebP, GIF)' })
    }
  }

  // Handle drag events
  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  // Handle file input change
  const handleInputChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  // Remove selected image
  const handleRemoveImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setResults(null)
    setError(null)
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!selectedImage) {
      setError({ message: 'Please select an image first' })
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      // Create FormData
      const formData = new FormData()
      formData.append('file', selectedImage)
      if (context.trim()) {
        formData.append('context', context.trim())
      }

      // Call backend API
      const response = await fetch('http://localhost:8000/generate-caption', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate captions')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError({ message: err.message || 'An unexpected error occurred' })
    } finally {
      setLoading(false)
    }
  }

  // Reset for new generation
  const handleNewGeneration = () => {
    setResults(null)
    setError(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🌟 AI Caption Generator</h1>
        <p>Upload an image and let AI create engaging captions, descriptions, and hashtags for your content</p>
      </header>

      {!results ? (
        <form onSubmit={handleSubmit}>
          {/* Upload Section */}
          <div
            className={`upload-section ${isDragging ? 'drag-active' : ''}`}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            {!selectedImage ? (
              <div className="upload-zone">
                <div className="upload-icon">📸</div>
                <p className="upload-text">
                  <strong>Click to upload</strong> or drag and drop
                </p>
                <p className="upload-subtext">
                  JPEG, PNG, WebP, or GIF (max 10MB)
                </p>
              </div>
            ) : (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" className="preview-img" />
                <p className="preview-name">{selectedImage.name}</p>
                <button
                  type="button"
                  className="remove-btn"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRemoveImage()
                  }}
                >
                  Remove Image
                </button>
              </div>
            )}
            
            <input
              id="file-input"
              type="file"
              accept="image/*"
              onChange={handleInputChange}
              className="file-input"
            />
          </div>

          {/* Context Input */}
          <div className="context-section">
            <label htmlFor="context" className="context-label">
              Context / Tone (Optional)
            </label>
            <textarea
              id="context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="e.g., professional, humorous, inspirational, casual..."
              className="context-input"
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="error">
              <div className="error-title">⚠️ Error</div>
              <div className="error-message">{error.message}</div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="submit-btn"
            disabled={!selectedImage || loading}
          >
            {loading ? 'Generating...' : '✨ Generate Captions'}
          </button>
        </form>
      ) : null}

      {/* Loading State */}
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p className="loading-text">Analyzing your image and generating content...</p>
        </div>
      )}

      {/* Results Display */}
      {results && !loading && (
        <div className="results">
          <div className="results-header">
            <h2>✅ Your Generated Content</h2>
            <p>Here are your AI-generated captions and hashtags</p>
          </div>

          <div className="results-grid">
            {/* Short Caption */}
            <div className="result-card">
              <h3>
                <span className="result-icon">📝</span>
                Short Caption
              </h3>
              <p className="result-content">{results.short_caption}</p>
            </div>

            {/* Long Description */}
            <div className="result-card">
              <h3>
                <span className="result-icon">📄</span>
                Long Description
              </h3>
              <p className="result-content">{results.long_description}</p>
            </div>

            {/* Hashtags */}
            <div className="result-card">
              <h3>
                <span className="result-icon">#️⃣</span>
                Hashtags
              </h3>
              <div className="hashtags">
                {results.hashtags.map((tag, index) => (
                  <span key={index} className="hashtag">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Call to Action */}
            <div className="result-card">
              <h3>
                <span className="result-icon">🎯</span>
                Call to Action
              </h3>
              <div className="cta-highlight">
                {results.cta}
              </div>
            </div>
          </div>

          {/* New Generation Button */}
          <button
            type="button"
            className="new-generation-btn"
            onClick={handleNewGeneration}
          >
            🔄 Generate New Captions
          </button>
        </div>
      )}
    </div>
  )
}

export default App

