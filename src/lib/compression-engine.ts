// Signal Compression Engine
// Compresses raw text input through 4 density layers

export interface CompressionResult {
  coreSignal: string;
  structurePoints: string[];
  emotionalResonance: string;
  inputTokens: number;
  outputTokens: number;
  compressionRatio: number;
}

interface TextAnalysis {
  sentences: string[];
  keywords: string[];
  tensions: string[];
  patterns: string[];
  emotionalValence: 'positive' | 'negative' | 'mixed' | 'neutral';
  dominantTheme: string;
}

function analyze(text: string): TextAnalysis {
  const sentences = text
    .replace(/([.!?])\s+/g, '$1|||')
    .split('|||')
    .map(s => s.trim())
    .filter(s => s.length > 3);

  // Extract keywords by frequency and position weight
  const stopWords = new Set([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
    'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
    'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
    'because', 'but', 'and', 'or', 'if', 'while', 'although', 'though',
    'that', 'this', 'these', 'those', 'it', 'its', 'i', 'me', 'my',
    'myself', 'we', 'our', 'ours', 'you', 'your', 'yours', 'he', 'him',
    'his', 'she', 'her', 'hers', 'they', 'them', 'their', 'what', 'which',
    'who', 'whom', 'am', 'about', 'up', 'down', 'also', 'like', 'really',
    'think', 'know', 'feel', 'get', 'got', 'go', 'going', 'make', 'much',
    'many', 'thing', 'things', 'even', 'still', 'way', 'want', 'don\'t',
    'doesn\'t', 'didn\'t', 'can\'t', 'won\'t', 'isn\'t', 'aren\'t',
    'wasn\'t', 'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t', 'couldn\'t',
    'wouldn\'t', 'shouldn\'t', 'let', 'say', 'said', 'keep', 'try',
    'something', 'anything', 'everything', 'nothing', 'someone',
  ]);

  const words = text.toLowerCase().replace(/[^a-z\s'-]/g, '').split(/\s+/).filter(w => w.length > 2);
  const freq: Record<string, number> = {};
  words.forEach(w => {
    if (!stopWords.has(w)) freq[w] = (freq[w] || 0) + 1;
  });
  const keywords = Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([w]) => w);

  // Detect tensions (opposing or contrasting concepts)
  const tensionPatterns = [
    /but\s+(.+?)(?:\.|,|$)/gi,
    /however\s+(.+?)(?:\.|,|$)/gi,
    /yet\s+(.+?)(?:\.|,|$)/gi,
    /although\s+(.+?)(?:\.|,|$)/gi,
    /despite\s+(.+?)(?:\.|,|$)/gi,
    /instead\s+(.+?)(?:\.|,|$)/gi,
    /rather\s+(.+?)(?:\.|,|$)/gi,
  ];
  const tensions: string[] = [];
  tensionPatterns.forEach(p => {
    let m;
    while ((m = p.exec(text)) !== null) {
      tensions.push(m[1].trim().slice(0, 80));
    }
  });

  // Detect structural patterns
  const patterns: string[] = [];
  if (sentences.length > 3 && keywords.length > 0) {
    const topKeyword = keywords[0];
    const mentionCount = words.filter(w => w === topKeyword).length;
    if (mentionCount > 2) patterns.push(`Recurring focus: "${topKeyword}" (${mentionCount}x)`);
  }
  if (tensions.length > 1) patterns.push(`Multiple tension points detected (${tensions.length})`);
  if (sentences.length > 5) patterns.push(`Extended elaboration pattern (${sentences.length} statements)`);
  
  // Detect repetition
  const uniqueWords = new Set(words.filter(w => !stopWords.has(w)));
  const repetitionRatio = uniqueWords.size / Math.max(words.length, 1);
  if (repetitionRatio < 0.4) patterns.push('High lexical repetition indicating circular reasoning');
  
  // Detect question pattern
  const questions = sentences.filter(s => s.includes('?'));
  if (questions.length > 1) patterns.push(`Inquiry-driven structure (${questions.length} questions)`);

  // Emotional valence
  const posWords = ['good', 'great', 'happy', 'love', 'wonderful', 'amazing', 'better', 'best', 'hope', 'excited', 'grateful', 'joy', 'success', 'progress', 'growth'];
  const negWords = ['bad', 'worse', 'worst', 'hate', 'terrible', 'awful', 'stuck', 'lost', 'confused', 'anxious', 'frustrated', 'overwhelmed', 'fail', 'struggle', 'fear', 'worry', 'stress', 'tired', 'exhausted', 'hopeless'];
  
  const posCount = words.filter(w => posWords.includes(w)).length;
  const negCount = words.filter(w => negWords.includes(w)).length;
  
  let emotionalValence: 'positive' | 'negative' | 'mixed' | 'neutral' = 'neutral';
  if (posCount > 0 && negCount > 0) emotionalValence = 'mixed';
  else if (posCount > negCount) emotionalValence = 'positive';
  else if (negCount > posCount) emotionalValence = 'negative';

  // Dominant theme from top keywords
  const dominantTheme = keywords.slice(0, 3).join(' / ') || 'unspecified';

  return { sentences, keywords, tensions, patterns, emotionalValence, dominantTheme };
}

function compressAt25(analysis: TextAnalysis, text: string): CompressionResult {
  const { sentences, keywords, emotionalValence } = analysis;
  
  // Plain clarity: summarize directly
  const keyPhrases = keywords.slice(0, 5);
  const coreSignal = sentences.length > 0
    ? sentences.slice(0, Math.min(3, sentences.length)).join(' ')
    : text.slice(0, 200);

  const structurePoints = [
    `Main topics: ${keyPhrases.join(', ')}`,
    `Contains ${sentences.length} distinct statements`,
    ...(analysis.tensions.length > 0 ? [`Notes contrasting elements: "${analysis.tensions[0]}"`] : []),
  ];

  const emotionalResonance = emotionalValence === 'neutral'
    ? 'Tone is measured and observational.'
    : emotionalValence === 'mixed'
    ? 'Tone carries both positive and negative currents.'
    : `Tone leans ${emotionalValence}.`;

  return {
    coreSignal,
    structurePoints,
    emotionalResonance,
    inputTokens: text.split(/\s+/).length,
    outputTokens: coreSignal.split(/\s+/).length,
    compressionRatio: Math.round((coreSignal.split(/\s+/).length / Math.max(text.split(/\s+/).length, 1)) * 100),
  };
}

function compressAt50(analysis: TextAnalysis, text: string): CompressionResult {
  const { keywords, tensions, emotionalValence, dominantTheme } = analysis;
  
  // Structured clarity
  const topKeywords = keywords.slice(0, 4);
  let coreSignal: string;
  
  if (tensions.length > 0) {
    coreSignal = `The input centers on ${dominantTheme}, presenting a tension between the stated situation and a desired or contrasting state. Core concern: ${topKeywords.slice(0, 2).join(' and ')}.`;
  } else {
    coreSignal = `The input articulates a position around ${dominantTheme}. Primary focus areas: ${topKeywords.join(', ')}.`;
  }

  const structurePoints = [
    `Dominant axis: ${topKeywords[0] || 'unidentified'}`,
    ...(tensions.length > 0 ? [`Tension: present state vs. implied alternative`] : []),
    `Elaboration density: ${analysis.sentences.length > 5 ? 'high' : analysis.sentences.length > 2 ? 'moderate' : 'low'}`,
    ...(keywords.length > 5 ? [`Secondary themes: ${keywords.slice(3, 6).join(', ')}`] : []),
  ];

  const emotionalResonance = emotionalValence === 'mixed'
    ? 'Ambivalence detected — coexistence of opposing emotional signals.'
    : emotionalValence === 'neutral'
    ? 'Emotional register is flat; cognitive framing dominates.'
    : `${emotionalValence === 'positive' ? 'Constructive' : 'Friction-bearing'} emotional undertone throughout.`;

  const inputTokens = text.split(/\s+/).length;
  const outputTokens = coreSignal.split(/\s+/).length;
  return {
    coreSignal,
    structurePoints,
    emotionalResonance,
    inputTokens,
    outputTokens,
    compressionRatio: Math.round((outputTokens / Math.max(inputTokens, 1)) * 100),
  };
}

function compressAt75(analysis: TextAnalysis, text: string): CompressionResult {
  const { keywords, tensions, patterns, emotionalValence, dominantTheme } = analysis;
  
  // Pattern articulation
  const mechanicDescriptors: string[] = [];
  
  if (tensions.length > 0) mechanicDescriptors.push('oscillation between states');
  if (patterns.some(p => p.includes('Recurring'))) mechanicDescriptors.push('recursive emphasis');
  if (patterns.some(p => p.includes('circular'))) mechanicDescriptors.push('closed-loop reasoning');
  if (patterns.some(p => p.includes('Inquiry'))) mechanicDescriptors.push('interrogative seeking');
  if (mechanicDescriptors.length === 0) mechanicDescriptors.push('linear assertion');

  const coreSignal = `The signal exhibits ${mechanicDescriptors.join(' and ')} around ${keywords[0] || 'its central axis'}. ${tensions.length > 0 ? `The dominant pattern is a gap between current state and projected resolution within the domain of ${dominantTheme}.` : `The pattern converges on ${dominantTheme} through ${analysis.sentences.length > 3 ? 'sustained elaboration' : 'direct assertion'}.`}`;

  const structurePoints = [
    `Structural mechanic: ${mechanicDescriptors[0]}`,
    `Signal density: ${keywords.length > 6 ? 'distributed across multiple nodes' : 'concentrated on few nodes'}`,
    ...patterns.slice(0, 3),
    ...(tensions.length > 1 ? ['Multi-axis tension: input contains more than one unresolved contrast'] : []),
  ];

  const emotionalResonance = emotionalValence === 'mixed'
    ? 'Emotional signal is dual-phased — constructive aspiration layered over friction.'
    : emotionalValence === 'neutral'
    ? 'Affective layer is suppressed; signal is predominantly structural.'
    : `${emotionalValence === 'positive' ? 'Forward momentum' : 'Resistance or constraint'} colors the structural pattern.`;

  const inputTokens = text.split(/\s+/).length;
  const outputTokens = coreSignal.split(/\s+/).length;
  return {
    coreSignal,
    structurePoints,
    emotionalResonance,
    inputTokens,
    outputTokens,
    compressionRatio: Math.round((outputTokens / Math.max(inputTokens, 1)) * 100),
  };
}

function compressAt100(analysis: TextAnalysis, text: string): CompressionResult {
  const { keywords, tensions, patterns, emotionalValence } = analysis;
  
  // System-level abstraction — distilled principle
  const hasTension = tensions.length > 0;
  const hasCircularity = patterns.some(p => p.includes('circular') || p.includes('Recurring'));
  const hasQuestions = patterns.some(p => p.includes('Inquiry'));
  const isExpanded = analysis.sentences.length > 5;

  let coreSignal: string;

  if (hasTension && hasCircularity) {
    coreSignal = `Sustained ${keywords[0] || 'cognitive'} intake without integration produces perceived stagnation. The system loops because resolution requires a mode shift the current framing cannot generate.`;
  } else if (hasTension && !hasCircularity) {
    coreSignal = `A structural gap between ${keywords[0] || 'current state'} and ${keywords[1] || 'desired state'} persists because the bridging mechanism remains unarticulated.`;
  } else if (hasCircularity && !hasTension) {
    coreSignal = `Recursive elaboration on ${keywords[0] || 'a single axis'} without external constraint produces diminishing conceptual returns.`;
  } else if (hasQuestions) {
    coreSignal = `The inquiry pattern indicates a search for framing rather than information — the system seeks not answers but the correct question.`;
  } else if (isExpanded) {
    coreSignal = `Extended articulation around ${keywords[0] || 'a focal point'} signals high investment in a structure that has not yet achieved self-compression.`;
  } else {
    coreSignal = `The signal maps a single vector: ${keywords[0] || 'assertion'} → ${keywords[1] || 'implication'}. Compression is already near-native; the input contains minimal redundancy.`;
  }

  // Structure points describe mechanics, not narrative
  const structurePoints: string[] = [];
  
  if (hasTension) structurePoints.push('Mechanic: state-gap without bridge function');
  if (hasCircularity) structurePoints.push('Mechanic: closed-loop iteration without exit condition');
  if (hasQuestions) structurePoints.push('Mechanic: frame-seeking through interrogative probing');
  if (isExpanded) structurePoints.push('Mechanic: elaboration exceeds structural necessity');
  if (!hasTension && !hasCircularity && !hasQuestions) structurePoints.push('Mechanic: direct assertion with minimal structural overhead');
  
  structurePoints.push(`Signal-to-noise: ${keywords.length > 6 ? 'distributed — multiple competing signals' : keywords.length > 3 ? 'focused — clear primary with secondary harmonics' : 'concentrated — minimal signal, high clarity'}`);

  // Emotional resonance as human grounding
  let emotionalResonance: string;
  if (emotionalValence === 'mixed') {
    emotionalResonance = 'The human behind this signal holds two truths simultaneously — this is not confusion but complexity.';
  } else if (emotionalValence === 'negative') {
    emotionalResonance = 'The weight here is real. The abstraction does not diminish the lived experience it encodes.';
  } else if (emotionalValence === 'positive') {
    emotionalResonance = 'Constructive intent grounds this signal — the abstraction points toward building, not merely analyzing.';
  } else {
    emotionalResonance = 'The signal is presented without emotional charge — the speaker prioritizes structure over sentiment.';
  }

  const inputTokens = text.split(/\s+/).length;
  const outputTokens = coreSignal.split(/\s+/).length;
  return {
    coreSignal,
    structurePoints,
    emotionalResonance,
    inputTokens,
    outputTokens,
    compressionRatio: Math.round((outputTokens / Math.max(inputTokens, 1)) * 100),
  };
}

export function compress(text: string, density: number): CompressionResult | null {
  if (!text.trim()) return null;
  
  const analysis = analyze(text);

  switch (density) {
    case 25: return compressAt25(analysis, text);
    case 50: return compressAt50(analysis, text);
    case 75: return compressAt75(analysis, text);
    case 100: return compressAt100(analysis, text);
    default: return compressAt50(analysis, text);
  }
}
