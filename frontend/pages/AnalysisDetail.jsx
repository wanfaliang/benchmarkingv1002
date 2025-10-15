// frontend/src/pages/AnalysisDetail.jsx
import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const AnalysisDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Analysis Detail Page</h1>
      <p>Analysis ID: {id}</p>
      <p>Coming soon...</p>
      <button onClick={() => navigate('/dashboard')} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>
        Back to Dashboard
      </button>
    </div>
  );
};

export default AnalysisDetail;
