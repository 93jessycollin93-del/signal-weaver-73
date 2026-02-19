import { useState, useCallback } from 'react';
import { compress, type CompressionResult } from '@/lib/compression-engine';
import { ChevronDown } from 'lucide-react';

const DENSITY_LABELS: Record<number, string> = {
  25: 'Plain clarity',
  50: 'Structured clarity',
  75: 'Pattern articulation',
  100: 'System-level abstraction',
};

const DENSITY_STEPS = [25, 50, 75, 100];

export default function SignalCompressor() {
  const [input, setInput] = useState('');
  const [density, setDensity] = useState(75);
  const [emotionalToggle, setEmotionalToggle] = useState(true);
  const [result, setResult] = useState<CompressionResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [expandedLayers, setExpandedLayers] = useState<Record<string, boolean>>({});

  const handleCompress = useCallback(() => {
    if (!input.trim()) return;
    setIsProcessing(true);
    // Simulate processing delay for feel
    setTimeout(() => {
      const r = compress(input, density);
      setResult(r);
      setIsProcessing(false);
      setExpandedLayers({});
    }, 400 + Math.random() * 300);
  }, [input, density]);

  const toggleLayer = (key: string) => {
    setExpandedLayers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const wordCount = input.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-baseline gap-3">
          <h1 className="font-mono text-sm font-semibold tracking-widest uppercase text-primary signal-glow">
            Signal Compression
          </h1>
          <span className="text-xs text-muted-foreground font-mono">v2.0</span>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-8 flex flex-col gap-8">
        {/* Input */}
        <section>
          <label className="block text-xs font-mono uppercase tracking-wider text-label mb-2">
            Input Signal
          </label>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Paste raw text, thoughts, or chaotic input here..."
            className="w-full h-40 bg-card border border-border rounded-sm px-4 py-3 text-sm text-foreground font-sans placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 resize-none transition-colors"
          />
          <div className="flex justify-between mt-1.5">
            <span className="text-xs font-mono text-muted-foreground">
              {wordCount} token{wordCount !== 1 ? 's' : ''}
            </span>
          </div>
        </section>

        {/* Controls */}
        <section className="flex flex-col gap-5">
          {/* Density Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-mono uppercase tracking-wider text-label">
                Density
              </label>
              <span className="text-xs font-mono text-primary">
                {density}% — {DENSITY_LABELS[density]}
              </span>
            </div>
            <div className="relative">
              <div className="h-1 rounded-full density-bar opacity-30" />
              <input
                type="range"
                min={25}
                max={100}
                step={25}
                value={density}
                onChange={e => setDensity(Number(e.target.value))}
                className="absolute inset-0 w-full h-1 opacity-0 cursor-pointer"
                style={{ margin: 0 }}
              />
              <div className="flex justify-between mt-1">
                {DENSITY_STEPS.map(s => (
                  <button
                    key={s}
                    onClick={() => setDensity(s)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      s <= density
                        ? 'bg-primary scale-100'
                        : 'bg-muted-foreground/30 scale-75'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Emotional Toggle + Compress */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setEmotionalToggle(!emotionalToggle)}
              className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-label hover:text-foreground transition-colors"
            >
              <span
                className={`w-7 h-4 rounded-full relative transition-colors ${
                  emotionalToggle ? 'bg-primary/40' : 'bg-muted'
                }`}
              >
                <span
                  className={`absolute top-0.5 w-3 h-3 rounded-full transition-all ${
                    emotionalToggle ? 'left-3.5 bg-primary' : 'left-0.5 bg-muted-foreground'
                  }`}
                />
              </span>
              Emotional Resonance
            </button>

            <button
              onClick={handleCompress}
              disabled={!input.trim() || isProcessing}
              className="px-5 py-2 bg-primary text-primary-foreground text-xs font-mono uppercase tracking-widest rounded-sm hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              {isProcessing ? 'Compressing...' : 'Compress Signal'}
            </button>
          </div>
        </section>

        {/* Output */}
        {result && (
          <section className="border-t border-border pt-6 flex flex-col gap-4">
            {/* Compression stats */}
            <div className="flex gap-6 text-xs font-mono text-muted-foreground">
              <span>{result.inputTokens} → {result.outputTokens} tokens</span>
              <span>{result.compressionRatio}% ratio</span>
            </div>

            {/* Core Signal */}
            <div className="surface-elevated border border-border rounded-sm p-5">
              <label className="block text-xs font-mono uppercase tracking-wider text-primary mb-3 signal-glow">
                Core Signal
              </label>
              <p className="text-sm leading-relaxed text-foreground">
                {result.coreSignal}
              </p>
            </div>

            {/* Structure Layer — collapsed by default */}
            <CollapsibleLayer
              title="Structure"
              expanded={!!expandedLayers['structure']}
              onToggle={() => toggleLayer('structure')}
            >
              <ul className="space-y-1.5">
                {result.structurePoints.map((point, i) => (
                  <li key={i} className="text-xs text-secondary-foreground font-mono flex gap-2">
                    <span className="text-muted-foreground select-none">›</span>
                    {point}
                  </li>
                ))}
              </ul>
            </CollapsibleLayer>

            {/* Emotional Resonance — collapsed by default */}
            {emotionalToggle && (
              <CollapsibleLayer
                title="Resonance"
                expanded={!!expandedLayers['resonance']}
                onToggle={() => toggleLayer('resonance')}
              >
                <p className="text-xs text-secondary-foreground leading-relaxed">
                  {result.emotionalResonance}
                </p>
              </CollapsibleLayer>
            )}
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border px-6 py-3">
        <div className="max-w-3xl mx-auto">
          <p className="text-xs font-mono text-muted-foreground/50">
            Input chaos → Compress → Stable insight → Human projection
          </p>
        </div>
      </footer>
    </div>
  );
}

function CollapsibleLayer({
  title,
  expanded,
  onToggle,
  children,
}: {
  title: string;
  expanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-border rounded-sm overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-2.5 text-xs font-mono uppercase tracking-wider text-label hover:text-foreground transition-colors"
      >
        {title}
        <ChevronDown
          className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
        />
      </button>
      {expanded && (
        <div className="px-4 pb-3 pt-0">
          {children}
        </div>
      )}
    </div>
  );
}
