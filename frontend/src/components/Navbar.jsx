import React, { useState } from 'react';
import { Globe, Phone, Menu, X, ArrowRight } from 'lucide-react';

export default function Navbar({ lang, setLang, t }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const languages = [
    { code: 'uz', label: "O'zbek", flag: 'UZ' },
    { code: 'ru', label: 'Русский', flag: 'RU' },
    { code: 'en', label: 'English', flag: 'EN' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full glass-panel border-b border-slate-200/90 bg-[#edf0f5]/90 backdrop-blur-md shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo normal size without any background container */}
          <a href="#" className="flex items-center group py-2">
            <img 
              src="/foundation-logo.png" 
              alt="Tashkent Tech Foundation Logo" 
              className="h-10 sm:h-12 w-auto object-contain transition-transform duration-200 group-hover:scale-105"
            />
          </a>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-8">
            <a 
              href="#about" 
              className="text-sm font-semibold text-slate-700 hover:text-[#e54519] transition-colors"
            >
              {t.nav.program}
            </a>
            <a 
              href="#subjects" 
              className="text-sm font-semibold text-slate-700 hover:text-[#e54519] transition-colors"
            >
              {t.nav.subjects}
            </a>
            <a 
              href="#apply-form" 
              className="text-sm font-semibold text-slate-700 hover:text-[#e54519] transition-colors"
            >
              {t.nav.apply}
            </a>
          </nav>

          {/* Right Action Bar: Phone + Language Toggle + CTA */}
          <div className="hidden lg:flex items-center gap-4">
            
            {/* Phone link */}
            <a 
              href={`tel:${t.nav.phone.replace(/\s+/g, '')}`}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-700 hover:text-[#e54519] hover:bg-slate-200/60 transition-all"
            >
              <Phone className="w-3.5 h-3.5 text-[#e54519]" />
              <span>{t.nav.phone}</span>
            </a>

            {/* Language Switcher */}
            <div className="flex items-center bg-white/90 p-1 rounded-xl border border-slate-300 shadow-sm">
              <Globe className="w-3.5 h-3.5 text-slate-500 ml-2 mr-1" />
              {languages.map((item) => (
                <button
                  key={item.code}
                  onClick={() => setLang(item.code)}
                  className={`px-2.5 py-1 text-xs font-bold rounded-lg transition-all ${
                    lang === item.code
                      ? 'bg-gradient-to-r from-orange-500 to-[#e54519] text-white shadow-sm shadow-orange-500/30'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                  aria-label={`Switch to ${item.label}`}
                >
                  {item.flag}
                </button>
              ))}
            </div>

            {/* Apply CTA */}
            <a
              href="#apply-form"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-[#e54519] to-orange-500 text-white shadow-md shadow-orange-600/25 hover:shadow-orange-600/40 hover:brightness-105 active:scale-95 transition-all"
            >
              <span>{t.nav.apply}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>

          {/* Mobile Right Controls */}
          <div className="flex items-center gap-2 lg:hidden">
            <div className="flex items-center bg-white/90 p-0.5 rounded-lg border border-slate-300 shadow-sm">
              {languages.map((item) => (
                <button
                  key={item.code}
                  onClick={() => setLang(item.code)}
                  className={`px-2 py-1 text-xs font-bold rounded-md ${
                    lang === item.code
                      ? 'bg-[#e54519] text-white'
                      : 'text-slate-600'
                  }`}
                >
                  {item.flag}
                </button>
              ))}
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-white border border-slate-300 text-slate-700 hover:text-black shadow-sm"
              aria-label="Toggle Menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-200 bg-white/95 backdrop-blur-xl px-4 py-5 space-y-4 shadow-lg animate-in slide-in-from-top duration-200">
          <div className="flex flex-col gap-3">
            <a 
              href="#about" 
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-semibold text-slate-800 hover:bg-slate-100"
            >
              {t.nav.program}
            </a>
            <a 
              href="#subjects" 
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm font-semibold text-slate-800 hover:bg-slate-100"
            >
              {t.nav.subjects}
            </a>
            <a 
              href={`tel:${t.nav.phone.replace(/\s+/g, '')}`}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold text-orange-600 hover:bg-slate-100"
            >
              <Phone className="w-4 h-4" />
              <span>{t.nav.phone}</span>
            </a>
          </div>

          <div className="pt-2 border-t border-slate-200">
            <a
              href="#apply-form"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold bg-[#e54519] text-white shadow-lg shadow-orange-600/30"
            >
              <span>{t.nav.apply}</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
