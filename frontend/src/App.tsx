import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Footer from './components/Footer';

// Pages
import Homepage from './pages/Homepage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CreateAnalysis from './pages/CreateAnalysis';
import AnalysisDetail from './pages/AnalysisDetail';
import SectionViewer from './pages/SectionViewer';
import GoogleCallback from './pages/GoogleCallback';
import VerifyEmail from './pages/VerifyEmail';
import RegistrationSuccess from './pages/RegistrationSuccess';
import Datasets from "./pages/Datasets";
import DatasetExplorer from "./pages/DatasetExplorer";
import DatasetsAdmin from "./pages/DatasetAdmin";
import CreateDataset from "./pages/CreateDataset";
import Datahubs from './pages/Datahubs';
import DatahubBuilder from './pages/DatahubBuilder';
import TreasuryExplorer from './pages/TreasuryExplorer';
import EconomicCalendar from './pages/EconomicCalendar';
import Research from './pages/Research';
import BLSLayout from './layouts/BLSLayout';
import BEALayout from './layouts/BEALayout';
import CUExplorer from './pages/bls/CUExplorer';
import LNExplorer from './pages/bls/LNExplorer';
import LAExplorer from './pages/bls/LAExplorer';
import CEExplorer from './pages/bls/CEExplorer';
import PCExplorer from './pages/bls/PCExplorer';
import WPExplorer from './pages/bls/WPExplorer';
import APExplorer from './pages/bls/APExplorer';
import CWExplorer from './pages/bls/CWExplorer';
import SMExplorer from './pages/bls/SMExplorer';
import JTExplorer from './pages/bls/JTExplorer';
import OEExplorer from './pages/bls/OEExplorer';
import ECExplorer from './pages/bls/ECExplorer';
import PRExplorer from './pages/bls/PRExplorer';
import TUExplorer from './pages/bls/TUExplorer';
import IPExplorer from './pages/bls/IPExplorer';
import SUExplorer from './pages/bls/SUExplorer';
import BDExplorer from './pages/bls/BDExplorer';
import EIExplorer from './pages/bls/EIExplorer';

// FRED Explorer Pages
import ClaimsExplorer from './pages/ClaimsExplorer';
import YieldCurveExplorer from './pages/YieldCurveExplorer';
import FedFundsExplorer from './pages/FedFundsExplorer';
import SentimentExplorer from './pages/SentimentExplorer';
import LeadingIndexExplorer from './pages/LeadingIndexExplorer';
import HousingExplorer from './pages/HousingExplorer';
import FREDCalendarExplorer from './pages/FREDCalendarExplorer';
import FREDReleasePage from './pages/FREDReleasePage';
import FREDSeriesPage from './pages/FREDSeriesPage';

// BEA Explorer Pages
import NIPAExplorer from './pages/NIPAExplorer';
import RegionalExplorer from './pages/RegionalExplorer';
import GDPbyIndustryExplorer from './pages/GDPbyIndustryExplorer';
import ITAExplorer from './pages/ITAExplorer';
import FixedAssetsExplorer from './pages/FixedAssetsExplorer';

// Stocks Module
import StocksPortal from './pages/stocks/StocksPortal';
import Screener from './pages/stocks/Screener';

// Create a client for react-query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App(): React.ReactElement {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <Router>
          <Header />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Homepage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/google/callback" element={<GoogleCallback />} />
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

            {/* Research Module */}
            <Route path="/research" element={<ProtectedRoute><Research /></ProtectedRoute>} />
            <Route path="/research/treasury" element={<ProtectedRoute><TreasuryExplorer /></ProtectedRoute>} />
            <Route path="/research/claims" element={<ProtectedRoute><ClaimsExplorer /></ProtectedRoute>} />
            <Route path="/research/fed-funds" element={<ProtectedRoute><FedFundsExplorer /></ProtectedRoute>} />
            <Route path="/research/sentiment" element={<ProtectedRoute><SentimentExplorer /></ProtectedRoute>} />
            <Route path="/research/leading" element={<ProtectedRoute><LeadingIndexExplorer /></ProtectedRoute>} />
            <Route path="/research/housing" element={<ProtectedRoute><HousingExplorer /></ProtectedRoute>} />
            <Route path="/research/yield-curve" element={<ProtectedRoute><YieldCurveExplorer /></ProtectedRoute>} />
            <Route path="/research/calendar" element={<ProtectedRoute><EconomicCalendar /></ProtectedRoute>} />
            <Route path="/research/fred-calendar" element={<ProtectedRoute><FREDCalendarExplorer /></ProtectedRoute>} />
            <Route path="/research/fred-calendar/release/:releaseId" element={<ProtectedRoute><FREDReleasePage /></ProtectedRoute>} />
            <Route path="/research/fred-calendar/series/:seriesId" element={<ProtectedRoute><FREDSeriesPage /></ProtectedRoute>} />

            {/* BEA Research Module - with layout */}
            <Route path="/research/bea" element={<ProtectedRoute><BEALayout /></ProtectedRoute>}>
              <Route path="nipa" element={<NIPAExplorer />} />
              <Route path="regional" element={<RegionalExplorer />} />
              <Route path="gdpbyindustry" element={<GDPbyIndustryExplorer />} />
              <Route path="ita" element={<ITAExplorer />} />
              <Route path="fixedassets" element={<FixedAssetsExplorer />} />
            </Route>

            {/* BLS Research Module - with layout */}
            <Route path="/research/bls" element={<ProtectedRoute><BLSLayout /></ProtectedRoute>}>
              <Route path="cu" element={<CUExplorer />} />
              <Route path="ln" element={<LNExplorer />} />
              <Route path="la" element={<LAExplorer />} />
              <Route path="ce" element={<CEExplorer />} />
              <Route path="pc" element={<PCExplorer />} />
              <Route path="wp" element={<WPExplorer />} />
              <Route path="ap" element={<APExplorer />} />
              <Route path="cw" element={<CWExplorer />} />
              <Route path="sm" element={<SMExplorer />} />
              <Route path="jt" element={<JTExplorer />} />
              <Route path="oe" element={<OEExplorer />} />
              <Route path="ec" element={<ECExplorer />} />
              <Route path="pr" element={<PRExplorer />} />
              <Route path="tu" element={<TUExplorer />} />
              <Route path="ip" element={<IPExplorer />} />
              <Route path="su" element={<SUExplorer />} />
              <Route path="bd" element={<BDExplorer />} />
              <Route path="ei" element={<EIExplorer />} />
            </Route>

            {/* Stocks Module */}
            <Route path="/stocks" element={<ProtectedRoute><StocksPortal /></ProtectedRoute>} />
            <Route path="/stocks/screener" element={<ProtectedRoute><Screener /></ProtectedRoute>} />

            {/* Catch all - redirect to home */}
            <Route path="*" element={<Navigate to="/" />} />

          </Routes>
          <Footer />
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
