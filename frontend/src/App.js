import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';  // NEW
import Footer from './components/Footer';  // NEW

// Pages
import Homepage from './pages/Homepage.jsx';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CreateAnalysis from './pages/CreateAnalysis';
import AnalysisDetail from './pages/AnalysisDetail';
import SectionViewer from './pages/SectionViewer';
import GoogleCallback from './pages/GoogleCallback';  // NEW
import VerifyEmail from './pages/VerifyEmail';
import RegistrationSuccess from './pages/RegistrationSuccess';
import Datasets from "./pages/Datasets";
import DatasetExplorer from "./pages/DatasetExplorer";
import DatasetsAdmin from "./pages/DatasetAdmin";
import CreateDataset from "./pages/CreateDataset";
import Datahubs from './pages/Datahubs';
import DatahubBuilder from './pages/DatahubBuilder';

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>  {/* NEW: Wrap with ThemeProvider */}
        <Router>
          <Header />  {/* NEW: Add Header */}
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Homepage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/google/callback" element={<GoogleCallback />} />  {/* NEW */}
            {/* NEW: Email verification routes */}
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/registration-success" element={<RegistrationSuccess />} />


            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis/create"
              element={
                <ProtectedRoute>
                  <CreateAnalysis />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis/:id"
              element={
                <ProtectedRoute>
                  <AnalysisDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analysis/:id/section/:sectionNum"
              element={
                <ProtectedRoute>
                  <SectionViewer />
                </ProtectedRoute>
              }
            />
            {/* Protected Dataset module */}
          <Route
            path="/datasets"
            element={
              <ProtectedRoute>
                <Datasets />
              </ProtectedRoute>
            }
          />
          <Route
            path="/datasets/:id"
            element={
              <ProtectedRoute>
                <DatasetExplorer />
              </ProtectedRoute>
            }
          />

          {/* Optional: role-guarded admin/tools */}
          <Route
            path="/admin/datasets"
            element={
              <ProtectedRoute roles={['admin']}>
                <DatasetsAdmin />
              </ProtectedRoute>
            }
          />
          <Route
            path="/datasets/new"
            element={
              <ProtectedRoute>
                <CreateDataset />
              </ProtectedRoute>
            }
          />
          <Route path="/datahubs" element={<ProtectedRoute><Datahubs /></ProtectedRoute>} />
          <Route path="/datahubs/:id" element={<ProtectedRoute><DatahubBuilder /></ProtectedRoute>} />
            {/* Catch all - redirect to home */}
            <Route path="*" element={<Navigate to="/" />} />
            
          </Routes>
          <Footer />  {/* NEW: Add Footer */}

        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;