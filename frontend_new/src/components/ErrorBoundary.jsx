import React from 'react';
import { AlertTriangle, Home } from 'lucide-react';
import { Button } from './Button';
import { Link } from 'react-router-dom';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught error in React Tree:", error, errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen w-full items-center justify-center bg-slate-900 p-6 text-slate-200">
          <div className="max-w-2xl nm-flat rounded-3xl p-10 border border-red-900/40 text-center flex flex-col items-center">
            <div className="nm-inset p-8 rounded-full bg-slate-950 mb-8">
              <AlertTriangle className="h-20 w-20 text-red-500 drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]" />
            </div>
            <h1 className="text-4xl font-black uppercase italic tracking-tighter text-white mb-4">Neural Link Severed</h1>
            <p className="text-slate-400 font-mono text-sm tracking-widest uppercase mb-8 max-w-md opacity-80 leading-relaxed">
              A critical failure occurred during UI rendering. The interface has entered safe mode to prevent system lockup.
            </p>
            
            <div className="w-full text-left bg-slate-950/50 rounded-xl p-4 border border-slate-800 mb-10 overflow-auto max-h-48 scrollbar-thin">
               <p className="text-red-400 font-mono text-[10px] mb-2 font-bold uppercase">Crash Dump:</p>
               <pre className="text-slate-500 font-mono text-[10px]">
                 {this.state.error && this.state.error.toString()}
                 <br/>
                 {this.state.errorInfo && this.state.errorInfo.componentStack}
               </pre>
            </div>

            <Button 
              size="lg" 
              onClick={() => window.location.href = '/'}
              className="px-12 h-14 text-sm tracking-[0.3em] nm-convex bg-slate-900 border-none text-white w-full uppercase"
            >
              <Home className="mr-3 h-5 w-5" /> REBOOT_INTERFACE
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
