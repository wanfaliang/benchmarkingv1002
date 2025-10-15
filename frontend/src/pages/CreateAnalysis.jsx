// frontend/src/pages/CreateAnalysis.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

const CreateAnalysis = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Create Analysis Page</h1>
      <p>Coming soon...</p>
      <button onClick={() => navigate('/dashboard')} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>
        Back to Dashboard
      </button>
    </div>
  );
};

export default CreateAnalysis;
