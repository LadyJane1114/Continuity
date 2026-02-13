import { useState } from 'react'
import mockAnalysisSegment from '../../components/TempAISub/AISub'
import EntityAnalysisCard from '../../components/ProjectLayout/EntityAnalysisCard';

const SegmentUpload = ({setSegments}) => {
    const [segment,setSegment] = useState("");
    const [analysis, setAnalysis] = useState(null);

    const handleSubmit = async(e) => {
        e.preventDefault();

        if (!segment.trim()) return;

        // later, send to main backend
        console.log(segment);
        const result = await mockAnalysisSegment(segment);
        setAnalysis(result);

        // Add new segment to app level state
        setSegments(prev => [...prev, {
            id: Date.now(),
            title: `Segment ${prev.length + 1}`,
            summary: result.summary,
            text: segment,
            entities: result.entities
        }])
    }

    const handleAccept = (entityId, factId) => {
        setAnalysis(prev => ({
            ...prev,
            entities: prev.entities.map(e => {
                if (e.id !== entityId) return e; // leave other entities unchanged

                return {
                    ...e,
                    facts: e.facts.map(f =>
                        f.id === factId ? { ...f, accepted: true } : f
                    )
                };
            })
        }));
    };

    const handleReject = (entityId, factId) => {
        setAnalysis(prev => ({
            ...prev,
            entities: prev.entities.map(e => {
                if (e.id !== entityId) return e;

                return {
                    ...e,
                    facts: e.facts.map(f =>
                        f.id === factId ? { ...f, accepted: false } : f
                    )
                };
            })
        }));
    };

    
  return (
    <>
    <form className='segmentUpload' onSubmit={handleSubmit}>
        <label htmlFor='userSegment'>Submit your Story Segment:</label>

        <textarea id='userSegment' 
                value={segment} 
                onChange={(e)=> setSegment(e.target.value)} 
                rows={10} 
                placeholder='Paste or type your text here...'
                maxLength={30000}
                />

        <div className='form-footer'>
            <div className='characterLength'>
                {segment.length} characters
            </div>
            <div>
                <button type='submit' disabled={!segment.trim()}>
                    Submit
                </button>
            </div>
        </div>
    </form>

    {/* Only render below if analysis exists */}
        {analysis && (
            <div className='segment-summary' style={{padding:"2rem", backgroundColor:"red",margin:"5px", borderRadius:"8px"} }>{analysis.summary}</div>
        )}
        {analysis && analysis.entities.map(entity => (
            <EntityAnalysisCard
                key={entity.id}
                entity={entity}
                editable={true}
                onAccept={handleAccept}
                onReject={handleReject}
            />
        ))}
    </>
  )
}

export default SegmentUpload