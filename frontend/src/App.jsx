import React, { useState, useEffect, lazy, Suspense } from 'react';
import Navbar from './components/Navbar';
import HeroBanner from './components/HeroBanner';
import ProgramHighlights from './components/ProgramHighlights';
import ApplicationForm from './components/ApplicationForm';
import Footer from './components/Footer';
import SubmissionModal from './components/SubmissionModal';
import EngineeringCanvas from './components/EngineeringCanvas';
import { translations } from './i18n/translations';

const ExcelExportPage = lazy(() => import('./components/ExcelExportPage'));

export default function App() {
  const [currentPath, setCurrentPath] = useState(() => {
    return typeof window !== 'undefined' ? window.location.pathname.toLowerCase() : '/';
  });

  const [lang, setLang] = useState(() => {
    return localStorage.getItem('tashtech_lang') || 'uz';
  });

  const [lastSubmission, setLastSubmission] = useState(null);

  useEffect(() => {
    const handleLocationChange = () => {
      setCurrentPath(window.location.pathname.toLowerCase());
    };
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  useEffect(() => {
    localStorage.setItem('tashtech_lang', lang);
    document.documentElement.lang = lang;
  }, [lang]);

  // Direct URL route: /excel (secret admin interface to view & download all leads)
  if (currentPath === '/excel' || currentPath === '/excel/') {
    return (
      <Suspense fallback={
        <div className="min-h-screen bg-[#edf0f5] flex items-center justify-center text-slate-500 font-sans">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Yuklanmoqda...</span>
          </div>
        </div>
      }>
        <ExcelExportPage />
      </Suspense>
    );
  }

  const t = translations[lang] || translations.uz;

  return (
    <div className="relative min-h-screen bg-[#edf0f5] text-slate-800 flex flex-col font-sans selection:bg-[#e54519] selection:text-white">
      
      {/* Interactive moving engineering canvas (Gears, formulas & particles) */}
      <EngineeringCanvas />

      {/* Sticky Navigation Header */}
      <Navbar lang={lang} setLang={setLang} t={t} />

      {/* Main Content */}
      <main className="flex-grow z-10">
        
        {/* Hero Section with Top Banner Image */}
        <HeroBanner t={t} />

        {/* 3 Core Subjects (Compact & concise) */}
        <ProgramHighlights t={t} />

        {/* Application & Question Intake Form */}
        <ApplicationForm 
          t={t} 
          lang={lang} 
          onSubmissionSuccess={(submission) => setLastSubmission(submission)} 
        />

      </main>

      {/* Footer */}
      <Footer t={t} />

      {/* Success Modal with Confetti & Telegram confirmation */}
      <SubmissionModal 
        submission={lastSubmission} 
        onClose={() => setLastSubmission(null)} 
        t={t} 
      />

    </div>
  );
}
