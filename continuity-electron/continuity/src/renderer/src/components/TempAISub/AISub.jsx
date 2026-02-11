

const mockAnalysisSegment = async (text) => {
    await delay(600);
    const words = text.split(/\s+/)


  return {
    summary: text.slice(0,140) + "...",
    entities: extractFakeEntities(words),
    facts: generateFakeFacts(text)
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


const generateFakeFacts = (text) => {
    const sentences = text
        .split(/[.!?]/)
        .map(s => s.trim())
        .filter(Boolean)
        .slice(0,4);

        return sentences.map(s => ({text: s, accepted:null }))
}


const delay= (ms) => {
    return new Promise(res => setTimeout(res, ms))
}

export default mockAnalysisSegment;