

const mockAnalysisSegment = async (text) => {
    await delay(600);
    const words = text.split(/\s+/)
    const entities = extractFakeEntities(words);
    const sentences = extractSentences(text);


  return {
    summary: text.slice(0,140) + "...",
    entities: buildMockEntities(entities, sentences)
  }
}

const extractFakeEntities = (words) => {
    const set = new Set();

    words.forEach(w => {
        if (/^[A-Z][a-z]+$/.test(w)) {
            set.add(w);
        }
    });
    return Array.from(set).slice(0, 6);
}

const extractSentences = (text) => {
    return text
        .split(/[.!?]/)
        .map(s => s.trim())
        .filter(Boolean)
        .slice(0,6)
}

const TYPES = ["Character", "Location", "Item", "Creature", "Organization", "Event"]

const buildMockEntities = (names, sentences) => {
    const safeNames = names.length > 0 ? names : ["Unknown"];

    let factId = 1;

        return safeNames.map((name, i) => {
            const facts = sentences
            .filter((_,idx)=> idx % safeNames.length === i % safeNames.length)
            .map(s => ({
                id: `f${factId++}`,
                text: s,
                accepted: null
            }))
        
        return {
            id: `e${i}`,
            name,
            type: TYPES[i % TYPES.length], // nonsense but stable
            aliases: [],
            facts
        }
    })
}

const delay= (ms) => {
    return new Promise(res => setTimeout(res, ms))
}

export default mockAnalysisSegment;