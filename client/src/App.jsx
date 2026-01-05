import React, { useState, useEffect } from 'react';
import { Folder, FileText, ChevronRight, ChevronDown, Menu, X, FileCode } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
});

// Component to render Mermaid diagrams
const Mermaid = ({ chart }) => {
  const [svg, setSvg] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    const renderChart = async () => {
      try {
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
        const { svg } = await mermaid.render(id, chart);
        setSvg(svg);
        setError(null);
      } catch (err) {
        console.error("Mermaid Render Error", err);
        setError("Failed to render diagram");
        // Mermaid might leave garbage in the DOM if it fails, ensuring cleanup is hard but recreating the component helps
      }
    };

    if (chart) {
      renderChart();
    }
  }, [chart]);

  if (error) return <div className="text-red-400 p-4 border border-red-500/30 rounded bg-red-500/10 text-sm font-mono">{error}</div>;
  return <div className="mermaid-container my-6 flex justify-center" dangerouslySetInnerHTML={{ __html: svg }} />;
};


// Sidebar Item Component
const FileTreeItem = ({ item, onSelect, depth = 0 }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [children, setChildren] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleToggle = async (e) => {
    e.stopPropagation();
    if (item.isDirectory) {
      if (!isOpen && !children) {
        setLoading(true);
        try {
          const res = await fetch(`http://localhost:3001/api/files?path=${encodeURIComponent(item.path)}`);
          const data = await res.json();
          setChildren(data.items);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      }
      setIsOpen(!isOpen);
    } else {
      onSelect(item);
    }
  };

  return (
    <div>
      <div
        className={`
                    flex items-center gap-2 py-1.5 px-3 cursor-pointer select-none
                    hover:bg-white/5 transition-colors text-sm
                    ${!item.isDirectory ? 'text-slate-400 hover:text-violet-300' : 'text-slate-200 font-medium'}
                `}
        style={{ paddingLeft: `${depth * 12 + 12}px` }}
        onClick={handleToggle}
      >
        {item.isDirectory ? (
          <span className="opacity-70">
            {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </span>
        ) : (
          <span className="w-3.5" /> // Spacer
        )}

        {item.isDirectory ? <Folder size={16} className="text-violet-400" /> : <FileText size={16} className="text-pink-400" />}
        <span className="truncate">{item.name}</span>
      </div>

      {isOpen && children && (
        <div>
          {children.map((child, idx) => (
            <FileTreeItem key={`${child.path}-${idx}`} item={child} onSelect={onSelect} depth={depth + 1} />
          ))}
        </div>
      )}

      {isOpen && loading && (
        <div className="pl-8 py-1 text-xs text-slate-600 animate-pulse">Loading...</div>
      )}
    </div>
  );
};


function App() {
  const [rootFiles, setRootFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [content, setContent] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Initial Load
  useEffect(() => {
    fetchFiles('C:/');
  }, []);

  const fetchFiles = async (path = '') => {
    try {
      const res = await fetch(`http://localhost:3001/api/files?path=${encodeURIComponent(path)}`);
      const data = await res.json();
      setRootFiles(data.items);
      setCurrentPath(data.currentPath);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    // Only load if markdown or text
    if (file.name.endsWith('.md') || file.name.endsWith('.txt') || file.name.endsWith('.json') || file.name.endsWith('.js')) {
      try {
        const res = await fetch(`http://localhost:3001/api/content?path=${encodeURIComponent(file.path)}`);
        const data = await res.json();
        setContent(data.content);
      } catch (err) {
        console.error(err);
        setContent('Error loading content');
      }
    } else {
      setContent(`Preview not available for ${file.name}`);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden text-slate-200 selection:bg-violet-500/30">
      {/* Sidebar */}
      <div className={`
                glass-panel w-80 flex-shrink-0 flex flex-col transition-all duration-300 ease-in-out border-r-0 border-r-white/5
                ${sidebarOpen ? 'translate-x-0' : '-translate-x-80 absolute z-10 h-full'}
            `}>
        <div className="h-14 flex items-center px-4 border-b border-white/5 gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500/50" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
          <div className="w-3 h-3 rounded-full bg-green-500/50" />
          <div className="flex-1" />
          <button onClick={() => setSidebarOpen(false)} className="p-1 hover:bg-white/10 rounded-md transition text-slate-400">
            <X size={14} />
          </button>
        </div>

        <div className="p-4 border-b border-white/5">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Explorer</h2>
          <div className="bg-black/20 p-2 rounded text-xs font-mono text-slate-400 truncate border border-white/5">
            {currentPath}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto py-2 custom-scrollbar">
          {rootFiles.map((file, idx) => (
            <FileTreeItem key={idx} item={file} onSelect={handleFileSelect} />
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col h-full bg-transparent relative transition-all duration-300 ${sidebarOpen ? '' : 'ml-0'}`}>
        {/* Header */}
        <div className="h-14 glass-panel border-b-0 flex items-center px-6 justify-between z-20">
          <div className="flex items-center gap-4">
            {!sidebarOpen && (
              <button onClick={() => setSidebarOpen(true)} className="p-2 hover:bg-white/10 rounded-lg transition text-slate-400">
                <Menu size={20} />
              </button>
            )}
            <h1 className="font-medium text-slate-200 flex items-center gap-2">
              {selectedFile ? (
                <>
                  <FileText size={18} className="text-violet-400" />
                  {selectedFile.name}
                </>
              ) : (
                <span className="text-slate-500 italic">No file selected</span>
              )}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-xs font-medium text-violet-300">
              Read Only
            </div>
          </div>
        </div>

        {/* Editor/Preview Area */}
        <div className="flex-1 overflow-hidden relative">
          {selectedFile ? (
            <div className="h-full overflow-y-auto p-8 lg:px-20 mx-auto max-w-5xl custom-scrollbar pb-32">
              {selectedFile.name.endsWith('.md') ? (
                <ReactMarkdown
                  className="markdown-body"
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '')
                      if (!inline && match && match[1] === 'mermaid') {
                        return <Mermaid chart={String(children).replace(/\n$/, '')} />
                      }
                      return !inline ? (
                        <pre className={className}>
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      )
                    }
                  }}
                >
                  {content}
                </ReactMarkdown>
              ) : (
                <pre className="font-mono text-sm text-slate-300 whitespace-pre-wrap">
                  {content}
                </pre>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-600">
              <FileCode size={64} className="mb-4 text-slate-700 opacity-50" />
              <p className="text-xl font-light">Select a markdown file to verify</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
