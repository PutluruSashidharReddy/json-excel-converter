import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
// Removed FaFileExcel to fix the warning
import { FaCloudUploadAlt, FaCheckCircle } from 'react-icons/fa'; 
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus('idle');
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/convert', formData, {
        responseType: 'blob', // Important for handling file downloads
      });

      // Create a link to download the file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'GSTR_Converted.xlsx');
      document.body.appendChild(link);
      link.click();
      
      setStatus('success');
      setTimeout(() => setStatus('idle'), 3000); // Reset after 3 seconds
    } catch (error) {
      console.error(error);
      setStatus('error');
    }
  };

  return (
    <div className="app-container">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h1>JSON to Excel Converter</h1>
        <p className="subtitle">Upload your GSTR JSON file below</p>

        <div className="upload-area">
          <input type="file" id="file" onChange={handleFileChange} accept=".json" hidden />
          <label htmlFor="file" className="file-label">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <FaCloudUploadAlt size={50} color="#4a90e2" />
              <p>{file ? file.name : "Click to Select JSON File"}</p>
            </motion.div>
          </label>
        </div>

        <AnimatePresence>
          {file && (
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="convert-btn"
              onClick={handleUpload}
              disabled={status === 'uploading'}
            >
              {status === 'uploading' ? 'Converting...' : 'Convert & Download'}
            </motion.button>
          )}
        </AnimatePresence>

        {status === 'success' && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="status-msg success"
          >
            <FaCheckCircle /> Success! Download started.
          </motion.div>
        )}
        
        {status === 'error' && (
          <p className="status-msg error">Error converting file.</p>
        )}
      </motion.div>
    </div>
  );
}

export default App;
