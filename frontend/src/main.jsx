import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { GoogleOAuthProvider } from '@react-oauth/google';

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

if (!googleClientId) {
  console.error("FATAL: VITE_GOOGLE_CLIENT_ID environment variable is not set.");
  // You could render an error message to the DOM here if desired
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={googleClientId || "YOUR_GOOGLE_CLIENT_ID_HERE_FALLBACK"}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
);
