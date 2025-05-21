import React, { useState } from 'react';

// Accept onTagsDetected as a prop
function ImageUploader({ onTagsDetected }) {
  const [selectedFile, setSelectedFile] = useState(null);
  // The detectedTags state is now primarily managed by App.jsx
  // This component can still keep a local version if needed for its own UI,
  // but the source of truth for App.jsx will be via onTagsDetected.
  // For this refactor, we'll call onTagsDetected and also update a local display state.
  const [localDetectedTags, setLocalDetectedTags] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    // Clear previous results and errors when a new file is selected
    setLocalDetectedTags([]);
    setErrorMessage(null);
    if (onTagsDetected) {
      onTagsDetected([]); // Also inform App.jsx that tags are cleared/reset
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select an image first.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setLocalDetectedTags([]); // Clear local tags
    if (onTagsDetected) {
      onTagsDetected([]); // Inform App.jsx to clear tags
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Assume backend is running on http://localhost:8000
      const response = await fetch('http://localhost:8000/api/suggest_video', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        const tags = data.detected_tags || [];
        setLocalDetectedTags(tags);
        if (onTagsDetected) {
          onTagsDetected(tags); // Pass tags up to App.jsx
        }
        if (tags.length === 0) {
          setErrorMessage('No food tags detected for the uploaded image.');
        }
      } else {
        const errorData = await response.json();
        setErrorMessage(errorData.detail || `Error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      setErrorMessage(error.message || 'A network error occurred. Ensure the backend server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Food Image Uploader</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={isLoading}>
        {isLoading ? 'Analyzing...' : 'Get Food Tags'}
      </button>

      {isLoading && <p>Loading tags...</p>}

      {errorMessage && <p style={{ color: 'red' }}>Error: {errorMessage}</p>}

      {/* Display localDetectedTags for immediate feedback within this component */}
      {localDetectedTags.length > 0 && (
        <div>
          <h4>Detected Tags:</h4>
          <ul>
            {localDetectedTags.map((tag, index) => (
              <li key={index}>{tag}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
