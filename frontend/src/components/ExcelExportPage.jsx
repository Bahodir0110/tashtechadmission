import React, { useState, useEffect, useMemo } from 'react';
import * as XLSX from 'xlsx';
import { 
  FileSpreadsheet, 
  Download, 
  RefreshCw, 
  Search, 
  Filter, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  Clock, 
  Users, 
  ExternalLink,
  ArrowLeft,
  Trash2,
  CheckSquare,
  Square
} from 'lucide-react';

export default function ExcelExportPage() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [deletingId, setDeletingId] = useState(null);
  const [bulkDeleting, setBulkDeleting] = useState(false);

  const fetchSubmissions = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiEndpoint = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api/submissions` 
        : '/api/submissions';
        
      const response = await fetch(`${apiEndpoint}?limit=10000`, {
        headers: { 'Accept': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error(`Server xatosi: ${response.status}`);
      }
      
      const data = await response.json();
      setSubmissions(Array.isArray(data) ? data : []);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message || "Arizalarni yuklashda xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions();
  }, []);

  // Filtered submissions based on search and status
  const filteredSubmissions = useMemo(() => {
    return submissions.filter(item => {
      // Status filter
      if (statusFilter !== 'ALL') {
        const itemStatus = item.status || 'Yangi';
        if (statusFilter === 'Aloqaga chiqildi' && itemStatus !== 'Aloqaga chiqildi') return false;
        if (statusFilter === 'Telefon ko\'tarilmadi' && itemStatus !== 'Telefon ko\'tarilmadi') return false;
        if (statusFilter === 'Bekor qildi' && itemStatus !== 'Bekor qildi') return false;
        if (statusFilter === 'Yangi' && item.status && item.status !== 'Yangi') return false;
      }

      // Search query filter
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase().trim();
      return (
        (item.full_name && item.full_name.toLowerCase().includes(q)) ||
        (item.phone && item.phone.toLowerCase().includes(q)) ||
        (item.telegram_username && item.telegram_username.toLowerCase().includes(q)) ||
        (item.school && item.school.toLowerCase().includes(q)) ||
        (item.region && item.region.toLowerCase().includes(q)) ||
        (item.question_text && item.question_text.toLowerCase().includes(q))
      );
    });
  }, [submissions, searchQuery, statusFilter]);

  // Statistics calculation
  const stats = useMemo(() => {
    const total = submissions.length;
    let contacted = 0;
    let noAnswer = 0;
    let cancelled = 0;
    let pending = 0;

    submissions.forEach(s => {
      if (s.status === 'Aloqaga chiqildi') contacted++;
      else if (s.status === 'Telefon ko\'tarilmadi') noAnswer++;
      else if (s.status === 'Bekor qildi') cancelled++;
      else pending++;
    });

    return { total, contacted, noAnswer, cancelled, pending };
  }, [submissions]);

  // Single delete handler
  const handleDeleteSingle = async (id, name) => {
    if (!window.confirm(`Haqiqatan ham #${id} - "${name}" arizasini o'chirmoqchimisiz?`)) {
      return;
    }
    setDeletingId(id);
    try {
      const apiEndpoint = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api/submissions/${id}` 
        : `/api/submissions/${id}`;
      const res = await fetch(apiEndpoint, { method: 'DELETE' });
      if (!res.ok) throw new Error("O'chirishda xatolik yuz berdi");
      setSubmissions(prev => prev.filter(s => s.id !== id));
      setSelectedIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    } catch (err) {
      alert(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  // Bulk delete handler
  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`Haqiqatan ham tanlangan ${selectedIds.size} ta arizani bazadan butunlay o'chirmoqchimisiz?`)) {
      return;
    }
    setBulkDeleting(true);
    try {
      const idsArray = Array.from(selectedIds);
      const apiEndpoint = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api/submissions/bulk-delete` 
        : `/api/submissions/bulk-delete`;
      const res = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: idsArray })
      });
      if (!res.ok) throw new Error("O'chirishda xatolik yuz berdi");
      setSubmissions(prev => prev.filter(s => !selectedIds.has(s.id)));
      setSelectedIds(new Set());
    } catch (err) {
      alert(err.message);
    } finally {
      setBulkDeleting(false);
    }
  };

  // Selection toggles
  const toggleSelectAll = () => {
    if (selectedIds.size === filteredSubmissions.length && filteredSubmissions.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredSubmissions.map(s => s.id)));
    }
  };

  const toggleSelectRow = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // Export to Microsoft Excel (.xlsx)
  const exportToExcel = () => {
    if (!submissions || submissions.length === 0) {
      alert("Yuklab olish uchun arizalar mavjud emas!");
      return;
    }

    const dataToExport = filteredSubmissions.length > 0 ? filteredSubmissions : submissions;

    const formattedRows = dataToExport.map(item => ({
      "ID": item.id,
      "F.I.Sh": item.full_name || "",
      "Telefon": item.phone || "",
      "Telegram": item.telegram_username || "",
      "Hudud / Viloyat": item.region || "",
      "Maktab / Litsey": item.school || "",
      "Savol / Izoh": item.question_text || "",
      "Holati": item.status || "Yangi",
      "Mas'ul xodim": item.contacted_by || "",
      "Bog'lanilgan vaqt": item.contacted_at ? new Date(item.contacted_at).toLocaleString('uz-UZ') : "",
      "Ariza topshirilgan sana": item.created_at ? new Date(item.created_at).toLocaleString('uz-UZ') : ""
    }));

    const worksheet = XLSX.utils.json_to_sheet(formattedRows);

    // Set column widths
    worksheet['!cols'] = [
      { wch: 6 },  // ID
      { wch: 32 }, // F.I.Sh
      { wch: 18 }, // Telefon
      { wch: 22 }, // Telegram
      { wch: 22 }, // Viloyat
      { wch: 32 }, // Maktab
      { wch: 40 }, // Savol / Izoh
      { wch: 24 }, // Holati
      { wch: 22 }, // Mas'ul
      { wch: 22 }, // Bog'lanilgan vaqt
      { wch: 24 }  // Ariza topshirilgan sana
    ];

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Arizalar");

    const dateStr = new Date().toISOString().split('T')[0];
    XLSX.writeFile(workbook, `TashTech_Foundation_Arizalar_${dateStr}.xlsx`);
  };

  // Export to CSV with UTF-8 BOM
  const exportToCsv = () => {
    if (!submissions || submissions.length === 0) {
      alert("Yuklab olish uchun arizalar mavjud emas!");
      return;
    }

    const dataToExport = filteredSubmissions.length > 0 ? filteredSubmissions : submissions;
    const headers = [
      "ID",
      "F.I.Sh",
      "Telefon",
      "Telegram",
      "Hudud / Viloyat",
      "Maktab / Litsey",
      "Savol / Izoh",
      "Holati",
      "Mas'ul xodim",
      "Bog'lanilgan vaqt",
      "Ariza topshirilgan sana"
    ];

    const escapeCsv = (val) => {
      if (val === null || val === undefined) return '""';
      const str = String(val).replace(/"/g, '""');
      return `"${str}"`;
    };

    const rows = dataToExport.map(item => [
      item.id,
      escapeCsv(item.full_name),
      escapeCsv(item.phone),
      escapeCsv(item.telegram_username),
      escapeCsv(item.region),
      escapeCsv(item.school),
      escapeCsv(item.question_text),
      escapeCsv(item.status || "Yangi"),
      escapeCsv(item.contacted_by || ""),
      escapeCsv(item.contacted_at ? new Date(item.contacted_at).toLocaleString('uz-UZ') : ""),
      escapeCsv(item.created_at ? new Date(item.created_at).toLocaleString('uz-UZ') : "")
    ].join(','));

    // \uFEFF ensures Excel properly decodes Uzbek Latin special characters (o', g')
    const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const dateStr = new Date().toISOString().split('T')[0];
    link.setAttribute('href', url);
    link.setAttribute('download', `TashTech_Foundation_Arizalar_${dateStr}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (status) => {
    if (status === 'Aloqaga chiqildi') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          Aloqaga chiqildi
        </span>
      );
    }
    if (status === 'Telefon ko\'tarilmadi') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
          <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
          Ko'tarilmadi
        </span>
      );
    }
    if (status === 'Bekor qildi') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
          <XCircle className="w-3.5 h-3.5 text-rose-600" />
          Bekor qildi
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300">
        <Clock className="w-3.5 h-3.5 text-slate-500" />
        Yangi
      </span>
    );
  };

  const allSelected = filteredSubmissions.length > 0 && selectedIds.size === filteredSubmissions.length;

  return (
    <div className="min-h-screen bg-[#edf0f5] text-slate-800 flex flex-col font-sans">
      
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <a href="/" className="flex items-center gap-2 group text-slate-500 hover:text-slate-800 transition-colors mr-2" title="Asosiy sahifaga qaytish">
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
            </a>
            <img 
              src="/foundation-logo.png" 
              alt="TashTech Foundation" 
              className="h-8 md:h-9 w-auto object-contain"
            />
            <div className="border-l border-slate-200 pl-3">
              <h1 className="text-base md:text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
                Arizalar bazasi & Excel Eksport
              </h1>
              <p className="text-xs text-slate-500">
                {lastUpdated ? `Oxirgi yangilanish: ${lastUpdated.toLocaleTimeString('uz-UZ')}` : 'Barcha arizalar to\'plami'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {selectedIds.size > 0 && (
              <button
                onClick={handleBulkDelete}
                disabled={bulkDeleting}
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs md:text-sm font-bold bg-rose-600 hover:bg-rose-700 text-white transition shadow-sm disabled:opacity-50 animate-in fade-in"
                title="Tanlangan barcha arizalarni o'chirish"
              >
                <Trash2 className="w-4 h-4" />
                <span>Tanlanganlarni o'chirish ({selectedIds.size})</span>
              </button>
            )}

            <button
              onClick={fetchSubmissions}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs md:text-sm font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition border border-slate-300 disabled:opacity-50"
              title="Ro'yxatni qayta yangilash"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Yangilash</span>
            </button>

            <button
              onClick={exportToCsv}
              disabled={loading || submissions.length === 0}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs md:text-sm font-medium bg-slate-800 hover:bg-slate-900 text-white transition shadow-sm disabled:opacity-50"
              title="CSV formatida yuklab olish"
            >
              <Download className="w-4 h-4" />
              <span>CSV</span>
            </button>

            <button
              onClick={exportToExcel}
              disabled={loading || submissions.length === 0}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs md:text-sm font-bold bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white transition shadow-md hover:shadow-lg disabled:opacity-50"
              title="Microsoft Excel (.xlsx) formatida yuklab olish"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Excel (.xlsx) yuklab olish</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex-grow space-y-6">

        {/* Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Jami arizalar</p>
              <p className="text-xl font-extrabold text-slate-900">{stats.total}</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Aloqaga chiqildi</p>
              <p className="text-xl font-extrabold text-emerald-700">{stats.contacted}</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Ko'tarilmadi</p>
              <p className="text-xl font-extrabold text-amber-700">{stats.noAnswer}</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
              <XCircle className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Bekor qilindi</p>
              <p className="text-xl font-extrabold text-rose-700">{stats.cancelled}</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-3 col-span-2 sm:col-span-1">
            <div className="w-10 h-10 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center font-bold">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Yangi (Kutilmoqda)</p>
              <p className="text-xl font-extrabold text-slate-800">{stats.pending}</p>
            </div>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="F.I.Sh, telefon, maktab, viloyat bo'yicha qidirish..."
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#e54519]/20 focus:border-[#e54519] transition"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-600"
              >
                Tozalash
              </button>
            )}
          </div>

          {/* Status Filters */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 text-xs">
            <span className="text-slate-400 flex items-center gap-1 mr-1 font-medium">
              <Filter className="w-3.5 h-3.5" /> Holat:
            </span>
            {[
              { id: 'ALL', label: `Barchasi (${stats.total})` },
              { id: 'Aloqaga chiqildi', label: `Aloqaga chiqildi (${stats.contacted})` },
              { id: "Telefon ko'tarilmadi", label: `Ko'tarilmadi (${stats.noAnswer})` },
              { id: 'Bekor qildi', label: `Bekor qildi (${stats.cancelled})` },
              { id: 'Yangi', label: `Yangi (${stats.pending})` }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition ${
                  statusFilter === tab.id
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-rose-500" />
              <span>{error}</span>
            </div>
            <button 
              onClick={fetchSubmissions} 
              className="text-xs font-semibold underline hover:no-underline"
            >
              Qayta urinish
            </button>
          </div>
        )}

        {/* Leads Table Container */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          
          <div className="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-3">
              <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Arizalar ro'yxati ({filteredSubmissions.length} ta ko'rsatilmoqda)
              </p>
              {selectedIds.size > 0 && (
                <span className="text-xs font-semibold text-rose-600 bg-rose-50 border border-rose-200 px-2.5 py-0.5 rounded-full">
                  {selectedIds.size} ta ariza tanlandi
                </span>
              )}
            </div>
            <span className="text-xs text-slate-500">
              Excel yuklanganda barcha {filteredSubmissions.length} ta yozuv kiritiladi
            </span>
          </div>

          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-100 text-slate-700 font-semibold sticky top-0 z-10 border-b border-slate-200">
                <tr>
                  <th className="py-3 px-3 w-10 text-center">
                    <button 
                      onClick={toggleSelectAll} 
                      className="text-slate-500 hover:text-slate-800 transition"
                      title={allSelected ? "Barchasini bekor qilish" : "Barchasini tanlash"}
                    >
                      {allSelected ? (
                        <CheckSquare className="w-4 h-4 text-emerald-600" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                  </th>
                  <th className="py-3 px-3 w-12 text-center">#</th>
                  <th className="py-3 px-4 min-w-[180px]">F.I.Sh</th>
                  <th className="py-3 px-4 min-w-[140px]">Telefon</th>
                  <th className="py-3 px-4 min-w-[140px]">Telegram</th>
                  <th className="py-3 px-4 min-w-[150px]">Viloyat / Hudud</th>
                  <th className="py-3 px-4 min-w-[180px]">Maktab / Litsey</th>
                  <th className="py-3 px-4 min-w-[200px]">Savol / Izoh</th>
                  <th className="py-3 px-4 min-w-[150px]">Holati</th>
                  <th className="py-3 px-4 min-w-[140px]">Mas'ul xodim</th>
                  <th className="py-3 px-4 min-w-[130px]">Topshirilgan vaqt</th>
                  <th className="py-3 px-3.5 w-16 text-center">Amal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={12} className="py-12 text-center text-slate-400">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-slate-400" />
                      Arizalar yuklanmoqda...
                    </td>
                  </tr>
                ) : filteredSubmissions.length === 0 ? (
                  <tr>
                    <td colSpan={12} className="py-12 text-center text-slate-400">
                      Hech qanday ariza topilmadi
                    </td>
                  </tr>
                ) : (
                  filteredSubmissions.map((item) => {
                    const formattedDate = item.created_at
                      ? new Date(item.created_at).toLocaleString('uz-UZ', {
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })
                      : '-';

                    const cleanTg = (item.telegram_username || '').replace(/^@/, '');
                    const isSelected = selectedIds.has(item.id);
                    const isDeleting = deletingId === item.id;

                    return (
                      <tr 
                        key={item.id} 
                        className={`transition-colors ${
                          isSelected ? 'bg-amber-50/70 hover:bg-amber-50' : 'hover:bg-slate-50'
                        }`}
                      >
                        <td className="py-3 px-3 text-center">
                          <button 
                            onClick={() => toggleSelectRow(item.id)}
                            className="text-slate-400 hover:text-slate-700 transition"
                          >
                            {isSelected ? (
                              <CheckSquare className="w-4 h-4 text-emerald-600" />
                            ) : (
                              <Square className="w-4 h-4" />
                            )}
                          </button>
                        </td>
                        <td className="py-3 px-3 text-center font-mono font-medium text-slate-400">
                          {item.id}
                        </td>
                        <td className="py-3 px-4 font-semibold text-slate-900">
                          {item.full_name}
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <a 
                            href={`tel:${item.phone}`} 
                            className="font-mono text-blue-600 hover:underline"
                          >
                            {item.phone}
                          </a>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          {cleanTg ? (
                            <a 
                              href={`https://t.me/${cleanTg}`} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              className="inline-flex items-center gap-1 text-sky-600 hover:underline"
                            >
                              @{cleanTg}
                              <ExternalLink className="w-3 h-3 opacity-60" />
                            </a>
                          ) : (
                            <span className="text-slate-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-slate-700">
                          {item.region}
                        </td>
                        <td className="py-3 px-4 text-slate-700">
                          {item.school}
                        </td>
                        <td className="py-3 px-4 text-slate-600 max-w-[220px] truncate" title={item.question_text || ''}>
                          {item.question_text || <span className="text-slate-300 italic">Izoh yo'q</span>}
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          {getStatusBadge(item.status)}
                        </td>
                        <td className="py-3 px-4 text-slate-600 whitespace-nowrap">
                          {item.contacted_by ? (
                            <div>
                              <span className="font-medium text-slate-800">{item.contacted_by}</span>
                              {item.contacted_at && (
                                <p className="text-[10px] text-slate-400 font-mono">
                                  {new Date(item.contacted_at).toLocaleDateString('uz-UZ')}
                                </p>
                              )}
                            </div>
                          ) : (
                            <span className="text-slate-300">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-500 whitespace-nowrap">
                          {formattedDate}
                        </td>
                        <td className="py-3 px-3.5 text-center">
                          <button
                            onClick={() => handleDeleteSingle(item.id, item.full_name)}
                            disabled={isDeleting}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition border border-transparent hover:border-rose-200"
                            title="Ushbu arizani o'chirish"
                          >
                            <Trash2 className={`w-3.5 h-3.5 ${isDeleting ? 'animate-spin' : ''}`} />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          <div className="p-4 border-t border-slate-200 bg-slate-50 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
            <span>
              Jami bazada: <strong className="text-slate-800">{submissions.length}</strong> ta ariza
            </span>
            <div className="flex items-center gap-2">
              {selectedIds.size > 0 && (
                <button
                  onClick={handleBulkDelete}
                  disabled={bulkDeleting}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold bg-rose-600 hover:bg-rose-700 text-white shadow-sm transition disabled:opacity-50"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Tanlangan {selectedIds.size} ta arizani o'chirish</span>
                </button>
              )}
              <button
                onClick={exportToExcel}
                disabled={loading || submissions.length === 0}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition disabled:opacity-50"
              >
                <FileSpreadsheet className="w-4 h-4" />
                <span>Barchasini Excel (.xlsx) ga yuklash</span>
              </button>
            </div>
          </div>

        </div>

      </main>

    </div>
  );
}
