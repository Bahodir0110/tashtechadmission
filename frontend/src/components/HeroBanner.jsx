import React from 'react';
import { ArrowRight, BookOpen, Sparkles, GraduationCap } from 'lucide-react';

export default function HeroBanner({ t }) {
  return (
    <section id="about" className="relative pt-6 pb-12 overflow-hidden">
      
      {/* Subtle warm ambient lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-orange-500/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Top Banner Frame */}
        <div className="relative group mb-12">
          <div className="absolute -inset-1 rounded-2xl sm:rounded-3xl bg-gradient-to-r from-orange-400 via-amber-400 to-orange-400 opacity-25 blur-md group-hover:opacity-40 transition duration-700" />
          
          <div className="relative rounded-2xl sm:rounded-3xl overflow-hidden bg-white border border-slate-300/80 shadow-xl">
            <img 
              src="/tashtech-banner.png" 
              alt="TashTech Foundation Program Banner" 
              className="w-full h-auto object-cover object-center max-h-[460px] transform hover:scale-[1.006] transition-transform duration-700"
            />
            
            {/* Minimal Corner Badges */}
            <div className="absolute top-3 left-3 sm:top-5 sm:left-5 flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wide bg-[#e54519] text-white shadow-md border border-orange-400/40">
                <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                100% BEPUL
              </span>
              <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/90 text-slate-800 shadow-sm border border-slate-200">
                <GraduationCap className="w-3.5 h-3.5 text-orange-500" />
                Constructor University (Germany)
              </span>
            </div>
          </div>
        </div>

        {/* Hero Editorial Section */}
        <div className="text-center max-w-4xl mx-auto">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-100 border border-orange-200 text-orange-700 text-xs sm:text-sm font-bold tracking-wide uppercase mb-6 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-[#e54519] animate-ping" />
            {t.hero.tagline}
          </div>

          {/* Heading strictly in 3 distinct lines:
              Line 1: "Abituriyentlar uchun"
              Line 2: "Tayyorlov kursi Foundation"
              Line 3: "Qabul ochildi!"
          */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 mb-6 leading-snug flex flex-col items-center">
            <span className="block text-slate-900 mb-1">
              {t.hero.line1}
            </span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-orange-600 via-[#e54519] to-amber-600 my-1 underline decoration-orange-500/40 decoration-wavy">
              {t.hero.line2}
            </span>
            <span className="block text-[#e54519] mt-1 font-black">
              {t.hero.line3}
            </span>
          </h1>

          {/* Subtitle / Description */}
          <p className="text-base sm:text-lg text-slate-600 font-normal leading-relaxed mb-8 max-w-3xl mx-auto">
            {t.hero.desc}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="#apply-form"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-base font-bold bg-gradient-to-r from-[#e54519] to-orange-500 text-white shadow-lg shadow-orange-600/30 hover:shadow-orange-600/40 hover:scale-[1.02] active:scale-95 transition-all"
            >
              <span>{t.hero.ctaApply}</span>
              <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="#subjects"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-4 rounded-xl text-base font-bold bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 shadow-sm transition-all"
            >
              <BookOpen className="w-5 h-5 text-orange-600" />
              <span>{t.hero.ctaLearnMore}</span>
            </a>
          </div>

        </div>

      </div>
    </section>
  );
}
