import { useState } from 'react'
import { reviewFact, submitReviewSession, uploadSegment } from '../../services/aiService';
import EntityAnalysisCard from '../../components/ProjectLayout/EntityAnalysisCard';
import LoadingOverlay from '../../components/ProjectLayout/LoadingOverlay';
import projectService from '../../services/projectService';

const SegmentUpload = ({setSegments}) => {
    const [segment,setSegment] = useState("");
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [submitError, setSubmitError] = useState(null);
    const [submitMessage, setSubmitMessage] = useState(null);
    const [isSubmittingReview, setIsSubmittingReview] = useState(false);

    const countPendingFacts = () => {
        if (!analysis) return 0;
        return analysis.entities.reduce((count, entity) => {
            return count + entity.facts.filter(f => f.accepted === null).length;
        }, 0);
    };

    const handleSubmit = async(e) => {
        e.preventDefault();

        if (!segment.trim()) return;

        setError(null);
        setSubmitError(null);
        setSubmitMessage(null);
        setLoading(true); // show the loading overlayyy
        try {
            const activeProject = await projectService.loadProject();
            if (!activeProject?.id) {
                throw new Error("No active project selected");
            }

            const result = await uploadSegment(activeProject.id, segment);
            setAnalysis(result);

            // Add new segment to app level state
            setSegments(prev => [...prev, {
                id: result.story?.id || Date.now(),
                title: result.story?.title || `Segment ${prev.length + 1}`,
                summary: result.summary,
                text: segment,
                entities: result.entities,
                reviewSessionId: result.reviewSessionId,
                pendingFactsCount: result.pendingFactsCount,
                conflictsDetected: result.conflictsDetected,
            }])
        } catch(error){
            console.error(error);
            setError(error.message || "Failed to upload segment");
        } finally {
            setLoading(false); // hide the overlay
        }


    }

    const handleAccept = async (entityId, factId) => {
        setSubmitError(null);
        try {
            await reviewFact(factId, "approved");
            setAnalysis(prev => ({
                ...prev,
                entities: prev.entities.map(e => {
                    if (e.id !== entityId) return e; // leave other entities unchanged

                    return {
                        ...e,
                        facts: e.facts.map(f =>
                            f.id === factId ? { ...f, accepted: true, status: "approved" } : f
                        )
                    };
                })
            }));
        } catch (err) {
            setSubmitError(err.message || "Failed to approve fact");
        }
    };

    const handleReject = async (entityId, factId) => {
        setSubmitError(null);
        try {
            await reviewFact(factId, "rejected");
            setAnalysis(prev => ({
                ...prev,
                entities: prev.entities.map(e => {
                    if (e.id !== entityId) return e;

                    return {
                        ...e,
                        facts: e.facts.map(f =>
                            f.id === factId ? { ...f, accepted: false, status: "rejected" } : f
                        )
                    };
                })
            }));
        } catch (err) {
            setSubmitError(err.message || "Failed to reject fact");
        }
    };

    const handleSubmitReview = async () => {
        if (!analysis?.reviewSessionId) {
            return;
        }

        setSubmitError(null);
        setSubmitMessage(null);
        setIsSubmittingReview(true);
        try {
            const result = await submitReviewSession(analysis.reviewSessionId);
            setSubmitMessage(result.message || "Review submitted");
        } catch (err) {
            setSubmitError(err.message || "Failed to submit review");
        } finally {
            setIsSubmittingReview(false);
        }
    };

    
  return (
    <>
    {/* loading overlay appears if segment is loading */}
    {loading && <LoadingOverlay/>}
    {error && <div className='segment-summary' style={{padding:"1rem", backgroundColor:"#511", margin:"5px", borderRadius:"8px", color:"#fff"}}>{error}</div>}
    {submitError && <div className='segment-summary' style={{padding:"1rem", backgroundColor:"#511", margin:"5px", borderRadius:"8px", color:"#fff"}}>{submitError}</div>}
    {submitMessage && <div className='segment-summary' style={{padding:"1rem", backgroundColor:"#154", margin:"5px", borderRadius:"8px", color:"#fff"}}>{submitMessage}</div>}

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
            <div className='segment-summary' style={{padding:"2rem", backgroundColor:"red",margin:"5px", borderRadius:"8px" }}>
                <div>{analysis.summary}</div>
                <div style={{marginTop: "0.5rem"}}>Pending facts: {analysis.pendingFactsCount || 0} | Conflicts: {analysis.conflictsDetected || 0}</div>
                <div style={{marginTop: "0.75rem"}}>
                    <button
                        type='button'
                        onClick={handleSubmitReview}
                        disabled={isSubmittingReview || countPendingFacts() > 0 || !analysis.reviewSessionId}
                    >
                        {isSubmittingReview ? "Submitting..." : "Submit Canon Decisions"}
                    </button>
                    {countPendingFacts() > 0 && <span style={{marginLeft: "0.5rem"}}>Resolve all facts before submit.</span>}
                </div>
            </div>
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