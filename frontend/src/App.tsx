import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Github, 
  Ticket, 
  Play, 
  Loader2, 
  CheckCircle2, 
  ChevronRight,
  Activity,
  Code,
  Settings,
  History,
  Terminal,
  Cpu,
  Layers,
  AlertCircle,
  Database,
  FileCheck,
  Code2,
  ShieldCheck,
  Eye,
  Search,
  Bell,
  Share2,
  FileCode,
  Check
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface Requirement {
  id: string;
  description: string;
  verdict: 'Pass' | 'Partial' | 'Fail' | 'Unknown';
  reasoning: string;
  evidence: string[];
}

interface EvaluationResult {
  jira_key: string;
  pr_url: string;
  overall_verdict: 'Pass' | 'Partial' | 'Fail' | 'Unknown';
  confidence_score: number;
  requirements: Requirement[];
  logs: string[];
}

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [jiraKey, setJiraKey] = useState('ENG-12903-AUTH-FIX');
  const [prUrl, setPrUrl] = useState('https://github.com/org/repo/pull/442');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState(0); // 0: Idle, 1: Retriever, 2: Parser, 3: Evaluator, 4: Verification, 5: Synthesis

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsEvaluating(true);
    setResult(null);
    setCurrentStep(1);
    setLogs(['[SYSTEM] Initializing evaluation pipeline...', '[AGENT] Spinning up orchestrator...']);

    try {
      // Simulate pipeline progression for UI visual
      setTimeout(() => setCurrentStep(2), 2000);
      setTimeout(() => setCurrentStep(3), 4000);
      setTimeout(() => setCurrentStep(4), 6000);

      const response = await axios.post(`${API_BASE}/evaluate`, {
        jira_key: jiraKey,
        pr_url: prUrl
      });
      
      setCurrentStep(5);
      setResult(response.data);
      if (response.data.logs) {
        setLogs(prev => [...prev, ...response.data.logs, '[SYSTEM] Evaluation complete.']);
      }
    } catch (error: any) {
      console.error(error);
      setLogs(prev => [...prev, `[ERROR] ${error.message}`]);
      setCurrentStep(0);
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="stitch-app">
      
      {/* 1. Sidebar */}
      <aside className="stitch-sidebar">
        <div className="flex items-center gap-3 px-2 mb-10">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--accent)' }}>
            <ShieldCheck className="text-white w-5 h-5" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">Evaluator</span>
        </div>

        <nav className="flex-1 flex flex-col gap-2">
          <a className="sidebar-link active" href="#">
            <Layers className="w-4 h-4" />
            <span>Dashboard</span>
          </a>
          <a className="sidebar-link" href="#">
            <History className="w-4 h-4" />
            <span>History</span>
          </a>
          <a className="sidebar-link" href="#">
            <Terminal className="w-4 h-4" />
            <span>Logs</span>
          </a>
          <a className="sidebar-link" href="#">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </a>
        </nav>

        <div className="mt-auto pt-4 border-t border-white/10">
          <div className="flex items-center gap-3 px-2 py-3">
            <div className="w-10 h-10 rounded-full bg-slate-700 overflow-hidden" style={{ border: '2px solid rgba(99, 102, 241, 0.2)' }}>
               <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex" alt="Avatar" />
            </div>
            <div className="text-xs">
              <p className="font-bold text-white">Dev Alex</p>
              <p className="text-slate-500">Premium Plan</p>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. Main Workspace */}
      <main className="stitch-main custom-scrollbar">
        <header className="h-16 border-b border-white/10 px-8 flex items-center justify-between sticky top-0 bg-[#0B0F19cc] backdrop-blur-md z-20">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-semibold text-slate-400">Project / Evaluator</h2>
            <span className="text-slate-600">/</span>
            <h1 className="text-sm font-medium text-white">Live Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={handleEvaluate}
              disabled={isEvaluating}
              className="stitch-button-primary"
            >
              {isEvaluating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              {isEvaluating ? 'Evaluating...' : 'Run Evaluation'}
            </button>
            <button className="p-2 text-slate-400 hover:text-white transition-all" style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
              <Bell className="w-5 h-5" />
            </button>
          </div>
        </header>

        <div className="p-8 flex flex-col gap-6 mx-auto w-full pb-24" style={{ maxWidth: '1400px' }}>
          
          {/* Inputs Section */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass-card p-5 flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">GitHub Pull Request URL</label>
              <div className="stitch-input-container">
                <Github className="w-4 h-4 text-slate-500" />
                <input 
                  className="stitch-input" 
                  value={prUrl}
                  onChange={(e) => setPrUrl(e.target.value)}
                  placeholder="Enter PR URL..."
                />
              </div>
            </div>
            <div className="glass-card p-5 flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Jira Ticket ID</label>
              <div className="stitch-input-container">
                <Ticket className="w-4 h-4 text-slate-500" />
                <input 
                  className="stitch-input" 
                  value={jiraKey}
                  onChange={(e) => setJiraKey(e.target.value)}
                  placeholder="Enter Jira ID..."
                />
              </div>
            </div>
          </section>

          {/* Pipeline Section */}
          <section className="glass-card p-8">
            <h3 className="text-xs font-bold text-slate-500 mb-10 uppercase tracking-widest">Agent Execution Pipeline</h3>
            <div className="flex items-center justify-between gap-2 px-10">
              {/* Retriever */}
              <div className="pipeline-node">
                <div className={`node-circle ${currentStep >= 1 ? 'completed' : ''} ${currentStep === 1 ? 'active' : ''}`}>
                  <Database className={`w-5 h-5 ${currentStep >= 1 ? 'text-white' : 'text-slate-500'}`} />
                  {currentStep >= 2 && (
                    <div className="absolute rounded-full border-2 flex items-center justify-center" style={{ bottom: '-4px', right: '-4px', width: '16px', height: '16px', backgroundColor: 'var(--success)', borderColor: 'var(--background)' }}>
                      <Check className="w-2.5 h-2.5 text-white" />
                    </div>
                  )}
                </div>
                <span className={`text-xs font-bold ${currentStep >= 1 ? 'text-white' : 'text-slate-500'} tracking-widest uppercase`}>Retriever</span>
              </div>

              <div className={`pipeline-connector ${currentStep >= 2 ? 'active' : ''}`} />

              {/* Parser */}
              <div className="pipeline-node">
                <div className={`node-circle ${currentStep >= 2 ? 'completed' : ''} ${currentStep === 2 ? 'active' : ''}`}>
                  <Code2 className={`w-5 h-5 ${currentStep >= 2 ? 'text-white' : 'text-slate-500'}`} />
                  {currentStep >= 3 && (
                    <div className="absolute rounded-full border-2 flex items-center justify-center" style={{ bottom: '-4px', right: '-4px', width: '16px', height: '16px', backgroundColor: 'var(--success)', borderColor: 'var(--background)' }}>
                      <Check className="w-2.5 h-2.5 text-white" />
                    </div>
                  )}
                </div>
                <span className={`text-xs font-bold ${currentStep >= 2 ? 'text-white' : 'text-slate-500'} tracking-widest uppercase`}>Parser</span>
              </div>

              <div className={`pipeline-connector ${currentStep >= 3 ? 'active' : ''}`} />

              {/* Evaluator */}
              <div className="pipeline-node">
                <div className={`node-circle ${currentStep >= 3 ? 'completed' : ''} ${currentStep === 3 ? 'active' : ''}`}>
                  <Cpu className={`w-5 h-5 ${currentStep >= 3 ? 'text-white' : 'text-slate-500'}`} />
                  {currentStep >= 4 && (
                    <div className="absolute rounded-full border-2 flex items-center justify-center" style={{ bottom: '-4px', right: '-4px', width: '16px', height: '16px', backgroundColor: 'var(--success)', borderColor: 'var(--background)' }}>
                      <Check className="w-2.5 h-2.5 text-white" />
                    </div>
                  )}
                </div>
                <span className={`text-xs font-bold ${currentStep >= 3 ? 'text-white' : 'text-slate-500'} tracking-widest uppercase`}>Evaluator</span>
              </div>

              <div className={`pipeline-connector ${currentStep >= 4 ? 'active' : ''}`} />

              {/* Verification */}
              <div className="pipeline-node">
                <div className={`node-circle ${currentStep >= 4 ? 'completed' : ''} ${currentStep === 4 ? 'active' : ''}`}>
                  <Layers className={`w-5 h-5 ${currentStep >= 4 ? 'text-white' : 'text-slate-500'}`} />
                  {currentStep >= 5 && (
                    <div className="absolute rounded-full border-2 flex items-center justify-center" style={{ bottom: '-4px', right: '-4px', width: '16px', height: '16px', backgroundColor: 'var(--success)', borderColor: 'var(--background)' }}>
                      <Check className="w-2.5 h-2.5 text-white" />
                    </div>
                  )}
                </div>
                <span className={`text-xs font-bold ${currentStep >= 4 ? 'text-white' : 'text-slate-500'} tracking-widest uppercase`}>Verification</span>
              </div>

              <div className={`pipeline-connector ${currentStep >= 5 ? 'active' : ''}`} />

              {/* Synthesis */}
              <div className="pipeline-node">
                <div className={`node-circle ${currentStep >= 5 ? 'completed' : ''} ${currentStep === 5 ? 'active' : ''}`}>
                  <FileCheck className={`w-5 h-5 ${currentStep >= 5 ? 'text-white' : 'text-slate-500'}`} />
                </div>
                <span className={`text-xs font-bold ${currentStep >= 5 ? 'text-white' : 'text-slate-500'} tracking-widest uppercase`}>Synthesis</span>
              </div>
            </div>
          </section>

          {/* Result Summary */}
          <AnimatePresence>
            {result && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
                <div className={`glass-card p-8 flex items-center justify-between ${result.overall_verdict === 'Pass' ? 'glow-success' : ''}`}>
                  <div className="flex items-center gap-10">
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">System Verdict</span>
                      <h2 className="verdict-text" style={{ color: result.overall_verdict === 'Pass' ? 'var(--success)' : 'var(--error)' }}>
                        {result.overall_verdict.toUpperCase()}
                      </h2>
                    </div>
                    <div className="h-16 w-px bg-white/10" />
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Confidence</span>
                      <h2 className="text-4xl font-bold text-white leading-none">
                        {Math.round(result.confidence_score * 100)}<span className="font-medium text-2xl" style={{ color: 'var(--accent)' }}>%</span>
                      </h2>
                    </div>
                  </div>
                  <div className="text-right flex flex-col items-end gap-2">
                    <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Analysis Time: 12.4s</p>
                    <div className="flex gap-1">
                      <div className="h-1.5 w-6 rounded-full" style={{ backgroundColor: 'var(--success)', boxShadow: '0 0 8px var(--success)' }} />
                      <div className="h-1.5 w-6 rounded-full" style={{ backgroundColor: 'var(--success)', boxShadow: '0 0 8px var(--success)' }} />
                      <div className="h-1.5 w-6 rounded-full" style={{ backgroundColor: 'var(--success)', boxShadow: '0 0 8px var(--success)' }} />
                      <div className="h-1.5 w-6 rounded-full bg-white/10" />
                    </div>
                  </div>
                </div>

                {/* Requirements Table */}
                <div className="glass-card overflow-hidden">
                  <div className="px-6 py-4 border-b border-white/10 bg-white/5 flex items-center justify-between">
                    <h4 className="text-sm font-bold text-white">Requirement Traceability</h4>
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-widest">{result.requirements.length} Criteria Identified</span>
                  </div>
                  <table className="stitch-table">
                    <thead>
                      <tr>
                        <th>Requirement ID</th>
                        <th>Description</th>
                        <th style={{ textAlign: 'center' }}>Status</th>
                        <th style={{ textAlign: 'right' }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.requirements.map((req, i) => (
                        <tr key={i}>
                          <td className="font-mono text-xs font-bold" style={{ color: 'var(--accent)' }}>{req.id}</td>
                          <td className="text-slate-200">{req.description}</td>
                          <td>
                            <div className="flex justify-center">
                              <span className={`status-badge ${req.verdict === 'Pass' ? 'pass' : 'fail'}`}>
                                {req.verdict === 'Pass' ? 'VERIFIED' : req.verdict === 'Fail' ? 'REJECTED' : 'UNCERTAIN'}
                              </span>
                            </div>
                          </td>
                          <td className="text-right">
                            <button className="text-slate-400 hover:text-white transition-all" style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
                              {req.verdict === 'Pass' ? <Eye className="w-4 h-4" /> : <Search className="w-4 h-4" />}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Visual Analysis Section */}
                <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Graph */}
                  <div className="glass-card p-6 h-[400px] flex flex-col">
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-8 flex items-center gap-2">
                      <Share2 className="w-3.5 h-3.5" /> Dependency Graph
                    </h4>
                    <div className="flex-1 border border-white/5 rounded-lg bg-surface flex items-center justify-center relative overflow-hidden" style={{ background: 'rgba(11, 15, 25, 0.4)' }}>
                       <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage: 'radial-gradient(#6366F1 1px, transparent 1px)', backgroundSize: '16px 16px'}} />
                       <div className="relative z-10 flex flex-col items-center gap-10">
                          <div className="p-3 bg-white/5 border border-white/10 rounded text-xs font-bold shadow-xl" style={{ color: 'var(--accent)', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
                            {result.requirements[0]?.id || 'REQ-MAIN'}
                          </div>
                          <div className="w-px h-10" style={{ backgroundColor: 'rgba(99, 102, 241, 0.3)' }} />
                          <div className="flex gap-4">
                            <div className="p-2 bg-surface border border-white/10 rounded text-xs text-slate-400">auth.service.ts</div>
                            <div className="p-2 bg-surface border border-white/10 rounded text-xs text-slate-400">login.routes.ts</div>
                          </div>
                       </div>
                    </div>
                  </div>

                  {/* Code View */}
                  <div className="glass-card flex flex-col h-[400px]">
                    <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between bg-white/5">
                      <div className="flex items-center gap-3">
                        <FileCode className="w-4 h-4" style={{ color: 'var(--accent)' }} />
                        <span className="text-xs font-bold text-white">src/services/auth.service.ts</span>
                        <span className="text-xs text-slate-500 bg-white/5 px-1.5 py-0.5 rounded">MODIFIED</span>
                      </div>
                    </div>
                    <div className="flex-1 overflow-auto p-4 diff-viewer leading-relaxed">
                       <div className="diff-line opacity-40">
                         <span className="diff-num">38</span>
                         <span>public async login(credentials: LoginDto) {'{'}</span>
                       </div>
                       <div className="diff-line opacity-40">
                         <span className="diff-num">39</span>
                         <span>  const user = await this.db.users.find(credentials.email);</span>
                       </div>
                       <div className="diff-line diff-add">
                         <span className="diff-num">40</span>
                         <span>+ // AI Evidence: Verification of REQ-101</span>
                       </div>
                       <div className="diff-line diff-add">
                         <span className="diff-num">41</span>
                         <span>+ if (user.status === 'ACTIVE') {'{'}</span>
                       </div>
                       <div className="diff-line diff-add">
                         <span className="diff-num">42</span>
                         <span>+   return this.redirectService.toDashboard(user.role);</span>
                       </div>
                    </div>
                  </div>
                </section>
              </motion.div>
            )}
          </AnimatePresence>

        </div>

        <footer className="h-14 mt-auto border-t border-white/10 flex items-center justify-center text-xs font-bold text-slate-600 tracking-widest uppercase opacity-50">
          Model: Gemini-2.0-Flash • Distributed Agent Protocol • v1.0.8
        </footer>

        {/* Floating Thinking Status */}
        {isEvaluating && (
          <div className="thinking-pill">
            <div className="status-dot animate-pulse" />
            <span className="text-xs font-bold text-white tracking-widest uppercase">
              {currentStep === 1 && 'Retriever: Fetching Context...'}
              {currentStep === 2 && 'Parser: Extracting Acceptance Criteria...'}
              {currentStep === 3 && 'Evaluator: Analyzing Logic...'}
              {currentStep === 4 && 'Verification: Running Tests...'}
              {currentStep === 5 && 'Synthesis: Finalizing Report...'}
            </span>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
