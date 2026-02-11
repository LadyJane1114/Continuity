import { useState } from 'react'
import mockAnalysisSegment from '../../components/TempAISub/AISub'
import EntityAnalysisCard from '../../components/ProjectLayout/EntityAnalysisCard';

const SegmentUpload = () => {
    const [segment,setSegment] = useState("");
    const [analysis, setAnalysis] = useState(null);

    const handleSubmit = async(e) => {
        e.preventDefault();

        if (!segment.trim()) return;

        // later, send to main backend
        console.log(segment);
        const result = await mockAnalysisSegment(segment);
        setAnalysis(result);

    }

    const handleAccept =(index) => {
        const newFacts = [... analysis.facts];
        newFacts[index].accepted = true;
        setAnalysis({...analysis, facts: newFacts});
    }

    const handleReject = (index) => {
        const newFacts = [...analysis.facts];
        newFacts[index].accepted = false;
        setAnalysis({ ...analysis, facts: newFacts });
    }
    
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
    {analysis && (
        <EntityAnalysisCard 
            entities={analysis.entities} 
            facts={analysis.facts} 
            editable={true} 
            onAccept={handleAccept} 
            onReject={handleReject}/>
    )}
    </>
  )
}

export default SegmentUpload