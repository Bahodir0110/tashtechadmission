import React from 'react';
import { Calculator, Atom, Languages, Cpu } from 'lucide-react';

export default function ProgramHighlights({ t }) {
  const subjectList = [
    {
      title: t.subjects.mathTitle,
      desc: t.subjects.mathDesc,
      icon: Calculator,
      topics: t.subjects.mathTopics,
      tag: 'STEM Core',
      gradient: 'from-orange-500/10 to-amber-500/5'
    },
    {
      title: t.subjects.physicsTitle,
      desc: t.subjects.physicsDesc,
      icon: Atom,
      topics: t.subjects.physicsTopics,
      tag: 'Engineering Base',
      gradient: 'from-orange-600/15 to-red-600/5'
    },
    {
      title: t.subjects.englishTitle,
      desc: t.subjects.englishDesc,
      icon: Languages,
      topics: t.subjects.englishTopics,
      tag: 'International',
      gradient: 'from-amber-600/10 to-orange-500/5'
    }
  ];

  return (
    <section id="subjects" className="py-12 relative overflow-hidden">
      
      {/* Decorative technical grid background */}
      <div className="absolute inset-0 bg-blueprint-grid opacity-35 pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Compact Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-100 border border-orange-200 text-orange-700 text-xs font-bold tracking-wider uppercase mb-3 shadow-sm">
            <Cpu className="w-3.5 h-3.5" />
            <span>TashTech Academic Standard</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
            {t.subjects.title}
          </h2>
          <p className="text-xs sm:text-sm text-slate-600">
            {t.subjects.subtitle}
          </p>
        </div>

        {/* 3 Compact Subject Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {subjectList.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={index}
                className="relative group rounded-2xl p-5 sm:p-6 bg-white/95 border border-slate-200/90 hover:border-orange-500/60 transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between overflow-hidden shadow-md shadow-slate-200/60"
              >
                {/* Glow accent */}
                <div className={`absolute top-0 right-0 w-28 h-28 bg-gradient-to-br ${item.gradient} rounded-full blur-xl pointer-events-none`} />

                <div>
                  {/* Top Bar with Icon and Tag */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-orange-500 to-[#e54519] flex items-center justify-center text-white shadow-md shadow-orange-500/25 group-hover:rotate-6 transition-transform">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-orange-50 text-orange-700 border border-orange-200">
                      {item.tag}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 mb-2 group-hover:text-orange-600 transition-colors">
                    {item.title}
                  </h3>

                  <p className="text-xs text-slate-600 leading-relaxed mb-4">
                    {item.desc}
                  </p>

                  {/* Compact topic chips */}
                  <div className="flex flex-wrap gap-1.5 pt-3 border-t border-slate-100">
                    {item.topics.map((topic, i) => (
                      <span 
                        key={i} 
                        className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-medium"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-5 pt-1">
                  <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-orange-500 to-[#e54519] w-2/3 rounded-full group-hover:w-full transition-all duration-500" />
                  </div>
                </div>

              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
