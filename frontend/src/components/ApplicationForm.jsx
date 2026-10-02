import React, { useState } from 'react';
import { Send, User, Phone, AtSign, MapPin, School, AlertCircle, MessageSquare, ShieldCheck, Sparkles } from 'lucide-react';

export default function ApplicationForm({ t, lang, onSubmissionSuccess }) {
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '+998 ',
    telegram_username: '',
    region: '',
    school: '',
    question_text: ''
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState(null);

  const validate = () => {
    const errs = {};
    if (!formData.full_name.trim() || formData.full_name.trim().length < 3) {
      errs.full_name = t.form.fullNameError;
    }

    const cleanPhone = formData.phone.replace(/[\s\-\(\)]/g, '');
    if (!cleanPhone || cleanPhone.length < 9) {
      errs.phone = t.form.phoneError;
    }

    if (!formData.telegram_username.trim()) {
      errs.telegram_username = t.form.telegramError;
    }

    if (!formData.region) {
      errs.region = t.form.regionError;
    }

    if (!formData.school.trim() || formData.school.trim().length < 2) {
      errs.school = t.form.schoolError;
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handlePhoneChange = (e) => {
    let val = e.target.value;
    if (!val.startsWith('+998')) {
      val = '+998 ' + val.replace(/^\+?998?/, '').trim();
    }
    setFormData((prev) => ({ ...prev, phone: val }));
    if (errors.phone) setErrors((prev) => ({ ...prev, phone: null }));
  };

  const handleTelegramChange = (e) => {
    let val = e.target.value;
    if (val && !val.startsWith('@') && !val.includes('t.me/')) {
      val = '@' + val;
    }
    setFormData((prev) => ({ ...prev, telegram_username: val }));
    if (errors.telegram_username) setErrors((prev) => ({ ...prev, telegram_username: null }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError(null);

    if (!validate()) {
      return;
    }

    setSubmitting(true);

    try {
      const apiEndpoint = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api/submissions` 
        : '/api/submissions';

      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Server error occurred');
      }

      const result = await response.json();
      
      onSubmissionSuccess(result);

      setFormData({
        full_name: '',
        phone: '+998 ',
        telegram_username: '',
        region: '',
        school: '',
        question_text: ''
      });
      setErrors({});
    } catch (err) {
      console.error('Submission failed:', err);
      setApiError(err.message || t.modal.errorDesc);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="apply-form" className="py-16 relative overflow-hidden">
      
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-[650px] h-[400px] bg-orange-500/8 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Form Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-orange-100 border border-orange-200 text-orange-700 text-xs font-bold uppercase tracking-wider mb-3 shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{t.form.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-3">
            {t.form.title}
          </h2>
          <p className="text-slate-600 text-sm sm:text-base max-w-2xl mx-auto">
            {t.form.subtitle}
          </p>
        </div>

        {/* Form Card in Grey/White Theme */}
        <div className="bg-white/95 p-6 sm:p-10 rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-300/40 relative overflow-hidden">
          
          {/* Top orange accent stripe */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-orange-500 via-[#e54519] to-amber-500" />

          {apiError && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-3 animate-in fade-in">
              <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-500" />
              <span>{apiError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* 1. Full Name */}
            <div>
              <label className="block text-xs sm:text-sm font-bold text-slate-800 mb-2">
                {t.form.fullNameLabel} <span className="text-[#e54519]">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <User className="w-5 h-5" />
                </div>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => {
                    setFormData({ ...formData, full_name: e.target.value });
                    if (errors.full_name) setErrors({ ...errors, full_name: null });
                  }}
                  placeholder={t.form.fullNamePlaceholder}
                  className={`w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-50 border ${
                    errors.full_name ? 'border-red-500 focus:border-red-500' : 'border-slate-300 focus:border-orange-500'
                  } text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:bg-white transition-all`}
                />
              </div>
              {errors.full_name && (
                <p className="mt-1.5 text-xs text-red-500 flex items-center gap-1 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  {errors.full_name}
                </p>
              )}
            </div>

            {/* 2 & 3. Phone + Telegram Username */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Phone */}
              <div>
                <label className="block text-xs sm:text-sm font-bold text-slate-800 mb-2">
                  {t.form.phoneLabel} <span className="text-[#e54519]">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Phone className="w-5 h-5" />
                  </div>
                  <input
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={handlePhoneChange}
                    placeholder={t.form.phonePlaceholder}
                    className={`w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-50 border ${
                      errors.phone ? 'border-red-500 focus:border-red-500' : 'border-slate-300 focus:border-orange-500'
                    } text-slate-900 placeholder-slate-400 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:bg-white transition-all`}
                  />
                </div>
                {errors.phone && (
                  <p className="mt-1.5 text-xs text-red-500 flex items-center gap-1 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" />
                    {errors.phone}
                  </p>
                )}
              </div>

              {/* Telegram Username */}
              <div>
                <label className="block text-xs sm:text-sm font-bold text-slate-800 mb-2">
                  {t.form.telegramLabel} <span className="text-[#e54519]">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <AtSign className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    required
                    value={formData.telegram_username}
                    onChange={handleTelegramChange}
                    placeholder={t.form.telegramPlaceholder}
                    className={`w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-50 border ${
                      errors.telegram_username ? 'border-red-500 focus:border-red-500' : 'border-slate-300 focus:border-orange-500'
                    } text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:bg-white transition-all`}
                  />
                </div>
                <p className="mt-1 text-[11px] text-slate-500">
                  {t.form.telegramHint}
                </p>
                {errors.telegram_username && (
                  <p className="mt-1 text-xs text-red-500 flex items-center gap-1 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" />
                    {errors.telegram_username}
                  </p>
                )}
              </div>

            </div>

            {/* 4. Region Dropdown */}
            <div>
              <label className="block text-xs sm:text-sm font-bold text-slate-800 mb-2">
                {t.form.regionLabel} <span className="text-[#e54519]">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <MapPin className="w-5 h-5" />
                </div>
                <select
                  required
                  value={formData.region}
                  onChange={(e) => {
                    setFormData({ ...formData, region: e.target.value });
                    if (errors.region) setErrors({ ...errors, region: null });
                  }}
                  className={`w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-50 border ${
                    errors.region ? 'border-red-500 focus:border-red-500' : 'border-slate-300 focus:border-orange-500'
                  } text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:bg-white transition-all appearance-none cursor-pointer`}
                >
                  <option value="" disabled className="text-slate-400">
                    -- {t.form.regionPlaceholder} --
                  </option>
                  {t.regions.map((reg, idx) => (
                    <option key={idx} value={reg} className="bg-white text-slate-900">
                      {reg}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-slate-500">
                  ▼
                </div>
              </div>
              {errors.region && (
                <p className="mt-1.5 text-xs text-red-500 flex items-center gap-1 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  {errors.region}
                </p>
              )}
            </div>

            {/* 5. In which school you study? */}
            <div>
              <label className="block text-xs sm:text-sm font-bold text-slate-800 mb-2">
                {t.form.schoolLabel} <span className="text-[#e54519]">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <School className="w-5 h-5" />
                </div>
                <input
                  type="text"
                  required
                  value={formData.school}
                  onChange={(e) => {
                    setFormData({ ...formData, school: e.target.value });
                    if (errors.school) setErrors({ ...errors, school: null });
                  }}
                  placeholder={t.form.schoolPlaceholder}
                  className={`w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-50 border ${
                    errors.school ? 'border-red-500 focus:border-red-500' : 'border-slate-300 focus:border-orange-500'
                  } text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:bg-white transition-all`}
                />
              </div>
              {errors.school && (
                <p className="mt-1.5 text-xs text-red-500 flex items-center gap-1 font-medium">
                  <AlertCircle className="w-3.5 h-3.5" />
                  {errors.school}
                </p>
              )}
            </div>

            {/* 6. Optional Question / Comment */}
            <div>
              <label className="block text-xs sm:text-sm font-bold text-slate-800 mb-2">
                {t.form.questionLabel}
              </label>
              <div className="relative">
                <div className="absolute top-3.5 left-0 pl-3.5 pointer-events-none text-slate-400">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <textarea
                  rows="3"
                  value={formData.question_text}
                  onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
                  placeholder={t.form.questionPlaceholder}
                  className="w-full pl-11 pr-4 py-3 rounded-xl bg-slate-50 border border-slate-300 focus:border-orange-500 text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:bg-white transition-all resize-none"
                />
              </div>
            </div>

            {/* Telegram Synchronization Notice */}
            <div className="p-4 rounded-xl bg-orange-50/80 border border-orange-200 flex items-start gap-3 text-xs text-slate-700 shadow-sm">
              <ShieldCheck className="w-5 h-5 text-[#e54519] flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-slate-900">
                  {t.form.telegramSyncNote}
                </p>
                <p className="text-slate-600 mt-0.5">
                  Tashkent University of Technology qabul komissiyasi arizangizni guruhda tezkorlik bilan qabul qiladi.
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className={`w-full py-4 rounded-xl text-base font-bold uppercase tracking-wider flex items-center justify-center gap-3 text-white transition-all duration-300 shadow-lg ${
                submitting
                  ? 'bg-slate-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-[#e54519] via-orange-500 to-amber-500 hover:brightness-105 shadow-orange-600/30 hover:shadow-orange-600/40 hover:scale-[1.01] active:scale-[0.99]'
              }`}
            >
              {submitting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>{t.form.submittingBtn}</span>
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>{t.form.submitBtn}</span>
                </>
              )}
            </button>

          </form>

        </div>

      </div>
    </section>
  );
}
