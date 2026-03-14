import React, { useState } from 'react';
import { 
  ClipboardCheck, 
  Github, 
  Ticket, 
  Play, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  XCircle,
  ChevronRight,
  Activity,
  Code
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

function App() {
  const [jiraKey, setJiraKey] = useState('');
  const [prUrl, setPrUrl] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsEvaluating(true);
    setResult(null);

    // TODO: Connect to backend API
    // For now, simulate evaluation
    setTimeout(() => {
      setResult({
        jira_key: jiraKey,
        pr_url: prUrl,
        overall_verdict: 'Partial',
        confidence_score: 0.85,
        requirements: [
          {
            id: 'REQ-1',
            description: 'Implement user authentication using JWT',
            verdict: 'Pass',
            reasoning: 'Authentication logic found in src/auth.ts and validated.',
            evidence: ['src/auth.ts:L45-L60']
          },
          {
            id: 'REQ-2',
            description: 'Add unit tests for the login flow',
            verdict: 'Fail',
            reasoning: 'No new test files found in the PR diff.',
            evidence: []
          }
        ],
        logs: [
          'Retriever: Fetched Jira PROJ-123 and GitHub PR #45',
          'Parser: Extracted 2 requirements from Jira description',
          'Evaluator: Comparing PR diff against requirements...',
          'Verification: Failed to find test evidence for REQ-2',
          'Synthesis: Evaluation complete.'
        ]
      });
      setIsEvaluating(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto">
      {/* Header */}
      <header className="flex items-center justify-between mb-12">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <ClipboardCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold gradient-text">Jira Ticket Evaluator</h1>
        </div>
        <div className="flex items-center gap-4 text-gray-400">
          <Github className="w-6 h-6 hover:text-white cursor-pointer transition-colors" />
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form & Status */}
        <div className="lg:col-span-12">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card mb-8"
          >
            <form onSubmit={handleEvaluate} className="flex flex-col md:flex-row gap-6 items-end">
              <div className="flex-1 space-y-2 w-full">
                <label className="text-sm font-medium text-gray-400 flex items-center gap-2">
                  <Ticket className="w-4 h-4" /> Jira Ticket Key
                </label>
                <input 
                  type="text" 
                  value={jiraKey}
                  onChange={(e) => setJiraKey(e.target.value)}
                  placeholder="e.g. PROJ-123"
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  required
                />
              </div>
              <div className="flex-1 space-y-2 w-full">
                <label className="text-sm font-medium text-gray-400 flex items-center gap-2">
                  <Github className="w-4 h-4" /> GitHub PR URL
                </label>
                <input 
                  type="url" 
                  value={prUrl}
                  onChange={(e) => setPrUrl(e.target.value)}
                  placeholder="https://github.com/user/repo/pull/45"
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  required
                />
              </div>
              <button 
                type="submit"
                disabled={isEvaluating}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-3 px-8 rounded-xl flex items-center gap-2 transition-all active:scale-95 whitespace-nowrap"
              >
                {isEvaluating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
                {isEvaluating ? 'Evaluating...' : 'Evaluate PR'}
              </button>
            </form>
          </motion.div>
        </div>

        {/* Evaluation Output Grid */}
        <AnimatePresence>
          {result && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="lg:col-span-12 grid grid-cols-1 lg:grid-cols-12 gap-8"
            >
              {/* Verdict Summary Card */}
              <div className="lg:col-span-4">
                <div className="glass-card h-full border-t-4 border-t-yellow-500">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold">Overall Verdict</h2>
                    <span className="px-3 py-1 bg-yellow-500/20 text-yellow-500 rounded-full text-xs font-bold tracking-wider uppercase">
                      {result.overall_verdict}
                    </span>
                  </div>
                  
                  <div className="flex flex-col items-center justify-center p-8 bg-black/20 rounded-2xl mb-6">
                    <div className="text-5xl font-bold mb-2">{(result.confidence_score * 100).toFixed(0)}%</div>
                    <div className="text-gray-400 text-sm uppercase tracking-widest">Confidence Score</div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                      </div>
                      <div className="text-sm">
                        <div className="font-bold">1/2 Requirements Met</div>
                        <div className="text-gray-400 text-xs">Based on line-by-line analysis</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Requirement Breakdown */}
              <div className="lg:col-span-8 flex flex-col gap-6">
                {result.requirements.map((req, idx) => (
                  <motion.div 
                    key={req.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="glass-card"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/5 rounded-lg border border-white/10">
                          <Activity className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                          <h3 className="font-bold text-lg">{req.description}</h3>
                          <span className="text-xs text-gray-500 font-mono">{req.id}</span>
                        </div>
                      </div>
                      <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold uppercase ${
                        req.verdict === 'Pass' ? 'bg-green-500/20 text-green-500' : 
                        req.verdict === 'Fail' ? 'bg-red-500/20 text-red-500' : 
                        'bg-yellow-500/20 text-yellow-500'
                      }`}>
                        {req.verdict === 'Pass' && <CheckCircle2 className="w-3 h-3" />}
                        {req.verdict === 'Fail' && <XCircle className="w-3 h-3" />}
                        {req.verdict === 'Partial' && <AlertCircle className="w-3 h-3" />}
                        {req.verdict}
                      </div>
                    </div>
                    
                    <p className="text-gray-400 text-sm mb-4 leading-relaxed italic">
                      " {req.reasoning} "
                    </p>

                    {req.evidence.length > 0 && (
                      <div className="flex items-center gap-2 pt-4 border-t border-white/5">
                        <Code className="w-4 h-4 text-gray-500" />
                        <div className="flex flex-wrap gap-2">
                          {req.evidence.map(ev => (
                            <span key={ev} className="text-[10px] font-mono bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20">
                              {ev}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing Logs */}
        {isEvaluating && (
          <div className="lg:col-span-12 mt-8">
            <div className="bg-black/80 border border-white/10 rounded-2xl p-6 font-mono text-sm">
              <div className="flex items-center gap-2 mb-4 text-blue-400">
                <Activity className="w-4 h-4 animate-pulse" />
                <span>Agent Execution Logs</span>
              </div>
              <div className="space-y-2 h-40 overflow-y-auto custom-scrollbar">
                {[
                  'Retriever: Fetched Jira PROJ-123 and GitHub PR #45',
                  'Parser: Extracted 2 requirements from Jira description',
                  'Evaluator: Comparing PR diff against requirements...',
                ].map((log, i) => (
                  <div key={i} className="flex gap-4 text-gray-500">
                    <span className="text-blue-500/50">[{new Date().toLocaleTimeString()}]</span>
                    <span>{log}</span>
                  </div>
                ))}
                <div className="flex gap-4 text-white animate-pulse">
                  <span className="text-blue-500/50">[{new Date().toLocaleTimeString()}]</span>
                  <span>Evaluator: Analyzing logical flow in src/auth.ts...</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
