import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Iridescence from './components/Iridescence';

const HomePage = lazy(() => import('./pages/HomePage'));
const ReportPage = lazy(() => import('./pages/ReportPage'));
const LeaderboardPage = lazy(() => import('./pages/LeaderboardPage'));
const ComparePage = lazy(() => import('./pages/ComparePage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));

function Loading() {
  return (
    <div style={{ textAlign: 'center', paddingTop: 80 }}>
      <div className="spinner" />
    </div>
  );
}

function App() {
  return (
    <>
      <Iridescence
        color={[0.33, 0.22, 0.55]}
        mouseReact={true}
        amplitude={0.06}
        speed={0.8}
        className="iridescence-bg"
      />
      <div style={{ position: 'relative', zIndex: 1 }}>
        <Navbar />
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/report/:repoId" element={<ReportPage />} />
            <Route path="/leaderboard" element={<LeaderboardPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </Suspense>
      </div>
    </>
  );
}

export default App;
