import { useState } from 'react';
import { useGoogleLogin, googleLogout } from '@react-oauth/google'; // Import googleLogout
import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import './App.css';
import ImageUploader from './ImageUploader';

function App() {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem('user');
    try {
      return storedUser ? JSON.parse(storedUser) : null;
    } catch (error) {
      console.error("Error parsing stored user:", error);
      localStorage.removeItem('user'); // Clear corrupted data
      return null;
    }
  });
  const [authError, setAuthError] = useState(null);
  const [youtubeActivity, setYoutubeActivity] = useState([]);
  const [youtubeLoading, setYoutubeLoading] = useState(false);
  const [youtubeError, setYoutubeError] = useState(null);

  // State for recommendations
  const [detectedTags, setDetectedTags] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [recommendationError, setRecommendationError] = useState(null);

  const googleLogin = useGoogleLogin({
    flow: 'auth-code',
    scope: 'openid email profile https://www.googleapis.com/auth/youtube.readonly',
    onSuccess: async (codeResponse) => {
      setAuthError(null);
      try {
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const backendResponse = await fetch(`${apiBaseUrl}/auth/google/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code: codeResponse.code }),
        });
        const data = await backendResponse.json();
        if (backendResponse.ok) {
          const userData = data; // Assuming 'data' is { message: "...", google_id: "...", email: "..." }
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData)); 
          console.log('Login successful:', userData);
        } else {
          setAuthError(data.detail || 'Login failed on backend.');
          setUser(null);
          localStorage.removeItem('user'); // Also clear on backend login failure
        }
      } catch (error) {
        setAuthError(error.message || 'An error occurred during login.');
        setUser(null);
        localStorage.removeItem('user'); // Clear on network/other errors
      }
    },
    onError: (errorResponse) => {
      console.error('Google Login Error:', errorResponse);
      if (errorResponse.type === 'popup_closed') {
        setAuthError('Login popup was closed before completing authentication.');
      } else {
        setAuthError(errorResponse.error_description || errorResponse.error || 'Google login failed.');
      }
      setUser(null);
      localStorage.removeItem('user'); // Clear on Google-side errors
    },
  });

  const handleSignOut = () => {
    googleLogout(); // Perform Google session logout
    localStorage.removeItem('user'); // Remove user from localStorage
    setUser(null); // Clear user state
    setAuthError(null); // Clear any auth errors
    setYoutubeActivity([]); // Clear youtube activity on sign out
    setYoutubeError(null); // Clear youtube errors on sign out
    setYoutubeLoading(false); // Reset loading state
    setRecommendations([]); // Clear recommendations on sign out
    setRecommendationError(null); // Clear recommendation errors
    setRecommendationLoading(false); // Reset recommendation loading state
    setRecommendations([]); // Clear recommendations on sign out
    setRecommendationError(null); // Clear recommendation errors
    setRecommendationLoading(false); // Reset recommendation loading state
    console.log('User signed out.');
  };

  const handleSignOut = async () => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    try {
      const response = await fetch(`${apiBaseUrl}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Backend logout failed:', errorData.detail || 'Unknown error');
        setAuthError(errorData.detail || 'Logout failed on server.'); 
      }
    } catch (error) {
      console.error('Error during backend logout:', error);
      setAuthError(error.message || 'Network error during logout.');
    } finally {
      googleLogout();
      localStorage.removeItem('user');
      setUser(null);
      setAuthError(null); 
      setDetectedTags([]); 
      setRecommendations([]); 
      setYoutubeActivity([]); 
      setYoutubeError(null);
      setYoutubeLoading(false);
      setRecommendationError(null);
      setRecommendationLoading(false);
      console.log('User signed out from frontend.');
    }
  };

  const fetchYouTubeActivity = async () => {
    if (!user) { // No need to check user.google_id as user object itself implies login
      setYoutubeError("Please sign in first to fetch YouTube activity.");
      return;
    }

    setYoutubeLoading(true);
    setYoutubeError(null);
    setYoutubeActivity([]);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/youtube_activity`, {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setYoutubeActivity(data);
        if (data.length === 0) {
            setYoutubeError("No liked videos found or activity is empty.");
        }
      } else {
        const errorData = await response.json();
        setYoutubeError(errorData.detail || "Failed to fetch YouTube activity.");
        setYoutubeActivity([]);
      }
    } catch (error) {
      setYoutubeError(error.message || "Network error while fetching YouTube activity.");
      setYoutubeActivity([]);
    } finally {
      setYoutubeLoading(false);
    }
  };

  return (
    <>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}> {/* Changed to column for logo + title */}
          <div className="logo-container" style={{ marginBottom: '0px' }}> 
            {/* Optional: Add a simple CSS-based play button icon here later if desired */}
            <span className="logo-text" style={{ 
              fontFamily: '"Open Sans", sans-serif', 
              fontWeight: 600, /* SemiBold */
              color: 'var(--neutral-dark-gray)', /* Use CSS variable */
              fontSize: '1.2rem' /* Adjusted size slightly */
            }}>
              SnackSync
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}> {/* Inner div for logos + h1 */}
            <a href="https://vite.dev" target="_blank" rel="noopener noreferrer">
              <img src={viteLogo} className="logo" alt="Vite logo" style={{ height: '3em', padding: '0.5em'}} />
            </a>
            <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
              <img src={reactLogo} className="logo react" alt="React logo" style={{ height: '3em', padding: '0.5em'}} />
            </a>
            <h1 style={{ marginLeft: '0.5rem', fontSize: '1.5rem', color: 'var(--primary-blue)' }}>Snacksy (Video Suggester)</h1> {/* Added brand color to h1 */}
          </div>
        </div>
        <div>
          {user ? (
            <div style={{ textAlign: 'right'}}>
              <p style={{ margin: 0, marginBottom: '0.25rem' }}>Welcome, {user.email || user.google_id}!</p>
              <button onClick={handleSignOut} style={{ padding: '0.5rem 1rem'}}>Sign Out</button>
            </div>
          ) : (
            <button onClick={() => googleLogin()} style={{ padding: '0.5rem 1rem'}}>
              Sign in with Google
            </button>
          )}
        </div>
      </header>

      <main style={{ padding: '1rem' }}>
        {authError && <p style={{ color: 'red' }}>Authentication Error: {authError}</p>}
        
        {/* Pass setDetectedTags to ImageUploader so it can update App's state */}
        {/* Also pass function to clear recommendations when new image is uploaded */}
        <ImageUploader 
          onTagsDetected={(tags) => {
            setDetectedTags(tags);
            setRecommendations([]); // Clear old recommendations when new tags are detected
            setRecommendationError(null);
          }} 
        />

        <hr style={{ margin: '2rem 0' }} />

        <div>
          <h2>Your YouTube Activity</h2>
          <button 
            onClick={fetchYouTubeActivity} 
            disabled={!user || youtubeLoading}
            style={{ padding: '0.5rem 1rem', marginBottom: '1rem' }}
          >
            {youtubeLoading ? 'Loading Activity...' : 'Fetch My Liked YouTube Videos'}
          </button>

          {youtubeLoading && <p>Loading YouTube activity...</p>}
          {youtubeError && <p style={{ color: 'red' }}>Error: {youtubeError}</p>}

          {youtubeActivity.length > 0 && (
            <div>
              <h3>My Liked Videos:</h3>
              {/* Removed inline listStyle and padding from ul, will be handled by .app-section ul or direct li styling */}
              <ul> 
                {youtubeActivity.map(video => (
                  <li key={video.id} className="video-item"> {/* Applied .video-item class */}
                    {video.thumbnail && <img src={video.thumbnail} alt={video.title} />} {/* Removed inline width, use CSS */}
                    <div className="video-item-content"> {/* Added content wrapper */}
                      <h4>
                        <a href={`https://www.youtube.com/watch?v=${video.id}`} target="_blank" rel="noopener noreferrer">
                          {video.title}
                        </a>
                      </h4>
                      <p>Channel: {video.channelTitle}</p>
                      <p>Duration: {video.duration} | Views: {video.viewCount}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {/* Optional: Message if activity is empty after a successful fetch but no error */}
          {!youtubeLoading && !youtubeError && youtubeActivity.length === 0 && user && 
           /* This condition ensures the message doesn't show initially or if there was an error */
           /* We also check if user is logged in to not show this before any attempt */
           ( <p>No liked videos found or activity is empty.</p> )
          }
        </div>

        <hr style={{ margin: '2rem 0' }} />

        <div>
          <h2>Video Recommendations</h2>
          <button
            onClick={handleGetRecommendations}
            disabled={!user || detectedTags.length === 0 || recommendationLoading}
            /* style removed, will use global button styles from App.css */
          >
            {recommendationLoading ? 'Getting Recommendations...' : 'Get Video Recommendations'}
          </button>

          {recommendationLoading && <p>Fetching recommendations...</p>}
          {recommendationError && <p style={{ color: 'red' }}>Error: {recommendationError}</p>}

          {recommendations.length > 0 && (
            <div>
              <h3>Recommended Videos:</h3>
              {recommendations.map(rec => (
                <div key={rec.video_id || rec.title} /* Use title as fallback key if video_id is missing */
                     style={{ border: '1px solid #ccc', margin: '10px', padding: '10px', borderRadius: '5px' }}>
                  <h4>
                    <a href={`https://www.youtube.com/watch?v=${rec.video_id}`} target="_blank" rel="noopener noreferrer">
                      {rec.title || rec.video_id}
                    </a>
                  </h4>
                  <p><b>Reason:</b> {rec.reason}</p>
                </div>
              ))}
            </div>
          )}
          {!recommendationLoading && !recommendationError && recommendations.length === 0 && user && detectedTags.length > 0 &&
            /* Show only if attempted and no results, not initially or if inputs are missing */
            (<p>No specific recommendations found for this combination. Try different food or broaden your YouTube activity!</p>)
          }
        </div>
      </main>
    </>
  );
}

// Helper function to be added for handleGetRecommendations
async function handleGetRecommendationsLogic(user, detectedTags, setRecommendationLoading, setRecommendationError, setRecommendations) {
  if (!user || !user.google_id) {
    setRecommendationError("Please sign in to get recommendations.");
    return;
  }
  if (!detectedTags || detectedTags.length === 0) {
    setRecommendationError("Please analyze a food image first to get tags.");
    return;
  }

  setRecommendationLoading(true);
  setRecommendationError(null);
  setRecommendations([]);

  try {
    const response = await fetch('http://localhost:8000/api/recommend_video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        food_tags: detectedTags,
        google_id: user.google_id,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      setRecommendations(data);
      if (data.length === 0) {
        // This message could be set here or handled by the conditional rendering logic
        // For now, conditional rendering handles "no recommendations found" message.
        console.log("No recommendations found for these tags/activity.");
      }
    } else {
      const errorData = await response.json();
      setRecommendationError(errorData.detail || "Failed to get recommendations.");
      setRecommendations([]);
    }
  } catch (error) {
    setRecommendationError(error.message || "Network error while fetching recommendations.");
    setRecommendations([]);
  } finally {
    setRecommendationLoading(false);
  }
}


  const handleGetRecommendations = async () => {
    if (!user) { // User object implies login, google_id is not directly needed for this check
      setRecommendationError("Please sign in to get recommendations.");
      return;
    }
    if (!detectedTags || detectedTags.length === 0) {
      setRecommendationError("Please analyze a food image first to get tags.");
      return;
    }

    setRecommendationLoading(true);
    setRecommendationError(null);
    setRecommendations([]);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/recommend_video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          food_tags: detectedTags, // google_id removed from body
        }),
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
        if (data.length === 0) {
          // This message is handled by the conditional rendering logic below
           setRecommendationError("No recommendations found for these tags/activity.");
        }
      } else {
        const errorData = await response.json();
        setRecommendationError(errorData.detail || "Failed to get recommendations.");
        setRecommendations([]);
      }
    } catch (error) {
      setRecommendationError(error.message || "Network error while fetching recommendations.");
      setRecommendations([]);
    } finally {
      setRecommendationLoading(false);
    }
  };

  return (
    <>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <a href="https://vite.dev" target="_blank" rel="noopener noreferrer">
            <img src={viteLogo} className="logo" alt="Vite logo" />
          </a>
          <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
            <img src={reactLogo} className="logo react" alt="React logo" />
          </a>
          <h1 style={{ marginLeft: '1rem', fontSize: '1.5rem' }}>Snacksy (Video Suggester)</h1>
        </div>
        <div>
          {user ? (
            <div style={{ textAlign: 'right'}}>
              <p style={{ margin: 0, marginBottom: '0.25rem' }}>Welcome, {user.email || user.google_id}!</p>
              <button onClick={handleSignOut} style={{ padding: '0.5rem 1rem'}}>Sign Out</button>
            </div>
          ) : (
            <button onClick={() => googleLogin()} style={{ padding: '0.5rem 1rem'}}>
              Sign in with Google
            </button>
          )}
        </div>
      </header>

      <main style={{ padding: '1rem' }}>
        {authError && <p style={{ color: 'red' }}>Authentication Error: {authError}</p>}
        
        <div className="app-section"> {/* ImageUploader Section */}
          <ImageUploader 
            onTagsDetected={(tags) => {
              setDetectedTags(tags);
              setRecommendations([]); 
              setRecommendationError(null);
            }} 
          />
        </div>

        {/* <hr style={{ margin: '2rem 0' }} />  Optional: hr can be removed if sections provide enough separation */}

        { user && ( /* Conditionally render YouTube Activity and Recommendations sections only if user is logged in */
          <>
            <div className="app-section"> {/* YouTube Activity Section */}
              <h2>Your YouTube Activity</h2>
              <button 
                onClick={fetchYouTubeActivity} 
            disabled={!user || youtubeLoading}
            style={{ padding: '0.5rem 1rem', marginBottom: '1rem' }}
          >
            {youtubeLoading ? 'Loading Activity...' : 'Fetch My Liked YouTube Videos'}
          </button>

          {youtubeLoading && <p>Loading YouTube activity...</p>}
          {youtubeError && <p style={{ color: 'red' }}>Error: {youtubeError}</p>}

          {youtubeActivity.length > 0 && (
            <div>
              <h3>My Liked Videos:</h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {youtubeActivity.map(video => (
                  <li key={video.id} style={{ borderBottom: '1px solid #eee', marginBottom: '1rem', paddingBottom: '1rem', display: 'flex', alignItems: 'flex-start' }}>
                    <img src={video.thumbnail} alt={video.title} width="120" style={{ marginRight: '1rem', flexShrink: 0 }} />
                    <div style={{ flexGrow: 1 }}>
                      <h4 style={{ marginTop: 0, marginBottom: '0.25rem' }}>{video.title}</h4>
                      <p style={{ fontSize: '0.9rem', margin: '0 0 0.25rem 0' }}>Channel: {video.channelTitle}</p>
                      <p style={{ fontSize: '0.8rem', margin: 0 }}>Duration: {video.duration} | Views: {video.viewCount}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {!youtubeLoading && !youtubeError && youtubeActivity.length === 0 && user && 
           ( <p>No liked videos found or activity is empty.</p> )
          }
        </div>

        {/* <hr style={{ margin: '2rem 0' }} /> Optional: hr can be removed */}

        <div className="app-section"> {/* Recommendations Section */}
          <h2>Video Recommendations</h2>
          <button
            onClick={handleGetRecommendations}
            disabled={!user || detectedTags.length === 0 || recommendationLoading}
            style={{ padding: '0.5rem 1rem', marginBottom: '1rem' }}
          >
            {recommendationLoading ? 'Getting Recommendations...' : 'Get Video Recommendations'}
          </button>

          {recommendationLoading && <p>Fetching recommendations...</p>}
          {recommendationError && <p style={{ color: 'red' }}>Recommendation Error: {recommendationError}</p>}

          {recommendations.length > 0 && (
            <div>
              <h3>Recommended Videos:</h3>
              {/* No outer ul needed if each item is a self-contained card */}
              {recommendations.map(rec => (
                <div key={rec.video_id || rec.title} className="recommendation-card"> {/* Applied .recommendation-card */}
                  {/* No image for recommendations as per current data structure from Gemini */}
                  <div className="video-item-content"> {/* Re-using for consistent text layout */}
                    <h4>
                      <a href={`https://www.youtube.com/watch?v=${rec.video_id}`} target="_blank" rel="noopener noreferrer">
                        {rec.title || rec.video_id}
                      </a>
                    </h4>
                    <p className="reasoning"><b>Reason:</b> {rec.reason}</p> {/* Applied .reasoning */}
                  </div>
                </div>
              ))}
            </div>
          )}
          {!recommendationLoading && !recommendationError && recommendations.length === 0 && user && detectedTags.length > 0 &&
            (<p>No specific recommendations found. Try different food or check your YouTube activity!</p>)
          }
        </div>
          </>
        )}
      </main>
    </>
  );
            disabled={!user || youtubeLoading}
            style={{ padding: '0.5rem 1rem', marginBottom: '1rem' }}
          >
            {youtubeLoading ? 'Loading Activity...' : 'Fetch My Liked YouTube Videos'}
          </button>

          {youtubeLoading && <p>Loading YouTube activity...</p>}
          {youtubeError && <p style={{ color: 'red' }}>Error: {youtubeError}</p>}

          {youtubeActivity.length > 0 && (
            <div>
              <h3>My Liked Videos:</h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {youtubeActivity.map(video => (
                  <li key={video.id} style={{ borderBottom: '1px solid #eee', marginBottom: '1rem', paddingBottom: '1rem', display: 'flex', alignItems: 'flex-start' }}>
                    <img src={video.thumbnail} alt={video.title} width="120" style={{ marginRight: '1rem', flexShrink: 0 }} />
                    <div style={{ flexGrow: 1 }}>
                      <h4 style={{ marginTop: 0, marginBottom: '0.25rem' }}>{video.title}</h4>
                      <p style={{ fontSize: '0.9rem', margin: '0 0 0.25rem 0' }}>Channel: {video.channelTitle}</p>
                      <p style={{ fontSize: '0.8rem', margin: 0 }}>Duration: {video.duration} | Views: {video.viewCount}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {!youtubeLoading && !youtubeError && youtubeActivity.length === 0 && user && 
           ( <p>No liked videos found or activity is empty.</p> )
          }
        </div>

        <hr style={{ margin: '2rem 0' }} />

        <div>
          <h2>Video Recommendations</h2>
          <button
            onClick={handleGetRecommendations}
            disabled={!user || detectedTags.length === 0 || recommendationLoading}
            style={{ padding: '0.5rem 1rem', marginBottom: '1rem' }}
          >
            {recommendationLoading ? 'Getting Recommendations...' : 'Get Video Recommendations'}
          </button>

          {recommendationLoading && <p>Fetching recommendations...</p>}
          {recommendationError && <p style={{ color: 'red' }}>Recommendation Error: {recommendationError}</p>}

          {recommendations.length > 0 && (
            <div>
              <h3>Recommended Videos:</h3>
              {recommendations.map(rec => (
                <div key={rec.video_id || rec.title} 
                     style={{ border: '1px solid #ccc', margin: '10px', padding: '10px', borderRadius: '5px' }}>
                  <h4>
                    <a href={`https://www.youtube.com/watch?v=${rec.video_id}`} target="_blank" rel="noopener noreferrer">
                      {rec.title || rec.video_id}
                    </a>
                  </h4>
                  <p><b>Reason:</b> {rec.reason}</p>
                </div>
              ))}
            </div>
          )}
          {!recommendationLoading && !recommendationError && recommendations.length === 0 && user && detectedTags.length > 0 &&
            (<p>No specific recommendations found. Try different food or check your YouTube activity!</p>)
          }
        </div>
      </main>
    </>
  );
}

export default App;

