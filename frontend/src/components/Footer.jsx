import React from 'react';
import { Phone, Mail, MapPin, ExternalLink, ShieldCheck } from 'lucide-react';

export default function Footer({ t }) {
  return (
    <footer className="border-t border-slate-300/80 bg-[#e2e8f0] relative z-10 pt-14 pb-10 text-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 pb-10 border-b border-slate-300">
          
          {/* Brand Info with Logo without background */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <img 
                src="/foundation-logo.png" 
                alt="Tashkent Tech Foundation Logo" 
                className="h-10 sm:h-11 w-auto object-contain"
              />
            </div>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
              {t.footer.aboutText}
            </p>
            <div className="flex items-center gap-2 text-xs text-[#e54519] font-bold">
              <ShieldCheck className="w-4 h-4" />
              <span>Constructor University hamkorligida</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-4">
              Bo'limlar
            </h4>
            <ul className="space-y-2 text-xs sm:text-sm text-slate-600">
              <li>
                <a href="#about" className="hover:text-[#e54519] transition-colors">
                  {t.nav.program}
                </a>
              </li>
              <li>
                <a href="#subjects" className="hover:text-[#e54519] transition-colors">
                  {t.nav.subjects}
                </a>
              </li>
              <li>
                <a href="#apply-form" className="hover:text-[#e54519] transition-colors">
                  {t.nav.apply}
                </a>
              </li>
              <li>
                <a 
                  href="https://tashkenttech-edu.uz/ru" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 hover:text-[#e54519] transition-colors font-medium"
                >
                  <span>{t.footer.officialSite}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </li>
            </ul>
          </div>

          {/* Contact Details */}
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-4">
              {t.footer.contactsTitle}
            </h4>
            <div className="space-y-3 text-xs sm:text-sm text-slate-600">
              <div className="flex items-start gap-3">
                <MapPin className="w-4 h-4 text-[#e54519] flex-shrink-0 mt-0.5" />
                <span>{t.footer.address}</span>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="w-4 h-4 text-[#e54519] flex-shrink-0" />
                <a href={`tel:${t.footer.phone.replace(/\s+/g, '')}`} className="hover:text-slate-900 transition-colors font-medium">
                  {t.footer.phone}
                </a>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="w-4 h-4 text-[#e54519] flex-shrink-0" />
                <a href={`mailto:${t.footer.email}`} className="hover:text-slate-900 transition-colors font-medium">
                  {t.footer.email}
                </a>
              </div>
            </div>
          </div>

        </div>

        {/* Copyright */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>
            © {new Date().getFullYear()} Tashkent University of Technology (TashTech). {t.footer.rights}
          </p>
          <p className="flex items-center gap-1">
            <span>Engineering Education Portal</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mx-1.5" />
            <span>FastAPI + aiogram Active</span>
          </p>
        </div>

      </div>
    </footer>
  );
}
