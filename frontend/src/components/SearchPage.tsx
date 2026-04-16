import { useState } from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from './LanguageContext';
import { Search, X, Download, Eye, Calendar, Loader2 } from 'lucide-react';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Button } from './ui/button';

export function SearchPage() {
  const { t, isRTL } = useLanguage();
  const [searchType, setSearchType] = useState('recorded');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [numPeople, setNumPeople] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [trackId, setTrackId] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);
      if (numPeople) params.append('num_people', numPeople);
      if (sessionId) params.append('session_id', sessionId);
      if (trackId) params.append('track_id', trackId);

      const response = await fetch(`http://localhost:8000/api/search?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setResults(data.results || []);
        setHasSearched(true);
      } else {
        setError(data.error || 'فشل البحث');
      }
    } catch (err) {
      console.error('خطأ:', err);
      setError('تأكد من تشغيل Backend');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setDateFrom('');
    setDateTo('');
    setNumPeople('');
    setSessionId('');
    setTrackId('');
    setResults([]);
    setHasSearched(false);
    setError('');
  };

  const handleExport = async () => {
    if (results.length === 0) return;
    
    try {
      const sessionIds = [...new Set(results.map(r => r.session_id))];
      const response = await fetch('http://localhost:8000/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_ids: sessionIds })
      });
      
      const data = await response.json();
      if (data.success) {
        const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `results_${Date.now()}.json`;
        a.click();
      }
    } catch (err) {
      console.error('خطأ:', err);
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/50 backdrop-blur-sm border border-cyan-500/20 rounded-xl p-6 shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-50" />
        
        <div className="flex items-center gap-3 mb-6">
          <Search className="text-cyan-400" size={24} />
          <h2 className="text-xl tracking-wide bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            {t.search.title}
          </h2>
        </div>

        <div className="mb-6">
          <Label className="text-gray-300 mb-3 block">{t.search.searchType}</Label>
          <RadioGroup value={searchType} onValueChange={setSearchType} className="flex gap-6">
            <div className="flex items-center gap-2">
              <RadioGroupItem value="recorded" id="recorded" />
              <Label htmlFor="recorded" className="text-gray-300">{t.search.recorded}</Label>
            </div>
            <div className="flex items-center gap-2">
              <RadioGroupItem value="live" id="live" />
              <Label htmlFor="live" className="text-gray-300">{t.search.live}</Label>
            </div>
          </RadioGroup>
        </div>

        <div className="mb-6">
          <Label className="text-gray-300 mb-3 block flex items-center gap-2">
            <Calendar size={16} className="text-cyan-400" />
            {t.search.dateTimeRange}
          </Label>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label className="text-gray-400 text-sm mb-2 block">{t.search.from}</Label>
              <Input
                type="datetime-local"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="bg-slate-800/50 border-cyan-500/30 text-gray-200"
              />
            </div>
            <div>
              <Label className="text-gray-400 text-sm mb-2 block">{t.search.to}</Label>
              <Input
                type="datetime-local"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="bg-slate-800/50 border-cyan-500/30 text-gray-200"
              />
            </div>
          </div>
        </div>

        <div className="mb-6">
          <Label className="text-gray-300 mb-3 block">{t.search.filters}</Label>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <Label className="text-gray-400 text-sm mb-2 block">{t.search.numPeople}</Label>
              <Input
                type="number"
                placeholder="0"
                value={numPeople}
                onChange={(e) => setNumPeople(e.target.value)}
                className="bg-slate-800/50 border-cyan-500/30 text-gray-200"
              />
            </div>
            <div>
              <Label className="text-gray-400 text-sm mb-2 block">{t.search.sessionId}</Label>
              <Input
                type="text"
                placeholder="SESSION-XXX"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="bg-slate-800/50 border-cyan-500/30 text-gray-200"
              />
            </div>
            <div>
              <Label className="text-gray-400 text-sm mb-2 block">{t.search.trackId}</Label>
              <Input
                type="text"
                placeholder="T-XXX"
                value={trackId}
                onChange={(e) => setTrackId(e.target.value)}
                className="bg-slate-800/50 border-cyan-500/30 text-gray-200"
              />
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <Button
            onClick={handleSearch}
            disabled={isLoading}
            className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 text-white"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin mr-2" /> : <Search size={16} className="mr-2" />}
            {t.search.searchButton}
          </Button>
          <Button onClick={handleClear} variant="outline" className="flex-1">
            <X size={16} className="mr-2" />
            {t.search.clearButton}
          </Button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-500/20 border border-red-500/40 rounded text-red-400 text-sm">
            ⚠️ {error}
          </div>
        )}
      </motion.div>

      {hasSearched && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900/50 backdrop-blur-sm border border-cyan-500/20 rounded-xl p-6 shadow-2xl"
        >
          <div className="mb-6">
            <h3 className="text-lg text-gray-300">
              {t.search.results} <span className="text-cyan-400 font-mono">({results.length})</span>
            </h3>
          </div>

          {results.length > 0 ? (
            <>
              <div className="space-y-3 mb-6 max-h-96 overflow-y-auto">
                {results.map((result, idx) => (
                  <div key={idx} className="bg-slate-800/50 border border-cyan-500/20 rounded-lg p-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-400 text-xs">Session:</span>
                        <p className="text-cyan-400 font-mono">{result.session_id}</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-xs">Frame:</span>
                        <p className="text-cyan-400 font-mono">{result.frame_number}</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-xs">People:</span>
                        <p className="text-green-400 font-mono">{result.person_count}</p>
                      </div>
                      <div>
                        <span className="text-gray-400 text-xs">Time:</span>
                        <p className="text-gray-300 font-mono text-xs">{new Date(result.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-4 pt-4 border-t border-cyan-500/20">
                <Button variant="outline" className="flex-1">
                  <Eye size={16} className="mr-2" />
                  {t.search.viewDetails}
                </Button>
                <Button onClick={handleExport} className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
                  <Download size={16} className="mr-2" />
                  {t.search.exportResults}
                </Button>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <Search className="text-gray-600 mx-auto mb-4" size={48} />
              <p className="text-gray-500">{t.search.noResults}</p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}