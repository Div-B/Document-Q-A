import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    <Toaster
      position="bottom-right"
      toastOptions={{
        style: {
          background: '#1f2937',
          color: '#f3f4f6',
          border: '1px solid #374151',
        },
        error: {
          duration: 5000,
        },
        success: {
          duration: 3000,
        },
      }}
    />
  </StrictMode>,
)
