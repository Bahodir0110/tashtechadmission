import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { CheckCircle2, Send, X, User, Phone, MapPin, School, AtSign } from 'lucide-react';

export default function SubmissionModal({ submission, onClose, t }) {
  useEffect(() => {
    if (submission) {
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#e54519', '#f97316', '#fbbf24', '#0f172a']
        });
      } catch (e) {
        // ignore
      }
    }
  }, [submission]);

  if (!submission) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-2xl animate-in zoom-in-95 duration-200 overflow-hidden">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Success Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4 shadow-sm border border-emerald-200">
            <CheckCircle2 className="w-9 h-9" />
          </div>

          <h3 className="text-2xl font-extrabold text-slate-900 mb-2">
            {t.modal.successTitle}
          </h3>
          <p className="text-sm text-slate-600">
            {t.modal.successDesc}
          </p>
        </div>

        {/* Summary Card */}
        <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200 space-y-3 mb-6 text-xs sm:text-sm">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <span className="text-slate-500 font-medium">{t.modal.idLabel}</span>
            <span className="font-mono font-bold text-[#e54519]">#{submission.id}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-500 flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-slate-400" />
              {t.modal.nameLabel}
            </span>
            <span className="font-bold text-slate-900">{submission.full_name}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-500 flex items-center gap-1.5">
              <Phone className="w-3.5 h-3.5 text-slate-400" />
              {t.modal.phoneLabel}
            </span>
            <span className="font-mono font-semibold text-slate-800">{submission.phone}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-500 flex items-center gap-1.5">
              <AtSign className="w-3.5 h-3.5 text-slate-400" />
              {t.modal.telegramLabel}
            </span>
            <span className="text-[#e54519] font-semibold">{submission.telegram_username}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-500 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {t.modal.regionLabel}
            </span>
            <span className="font-medium text-slate-800">{submission.region}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-500 flex items-center gap-1.5">
              <School className="w-3.5 h-3.5 text-slate-400" />
              {t.modal.schoolLabel}
            </span>
            <span className="font-semibold text-slate-800 truncate max-w-[220px]">{submission.school}</span>
          </div>

          {submission.telegram_sent && (
            <div className="pt-2 border-t border-slate-200 flex items-center gap-2 text-xs font-semibold text-emerald-600">
              <Send className="w-3.5 h-3.5" />
              <span>Telegram guruhiga muvaffaqiyatli yetkazildi!</span>
            </div>
          )}
        </div>

        {/* Next step notice */}
        <p className="text-xs text-slate-500 text-center mb-6 leading-relaxed">
          {t.modal.nextSteps}
        </p>

        {/* Action Button */}
        <button
          onClick={onClose}
          className="w-full py-3.5 rounded-xl font-bold bg-[#e54519] hover:bg-orange-600 text-white shadow-md shadow-orange-600/30 transition-all active:scale-95"
        >
          {t.modal.closeBtn}
        </button>

      </div>
    </div>
  );
}
