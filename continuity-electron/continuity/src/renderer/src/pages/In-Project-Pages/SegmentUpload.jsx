import { useState } from 'react'
// import TestModal from '@renderer/components/ProjectPage/TestModal';

const SegmentUpload = () => {
    const [segment,setSegment] = useState("");
    // const [showModal, setShowModal] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!segment.trim()) return;

        // later, send to main backend
        console.log(segment);
        
        //show simulation modal
        setShowModal(true);
    }
    // const handleCloseModal = () => {
    //     setShowModal(false);
    //     setSegment(""); // optional: clear textarea after submit
    // }
    
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

    {/* Modal for simulation purposes only */}
          {/* {showModal && (
              <TestModal
                  message="You submitted your text!"
                  onClose={handleCloseModal}
              />
          )} */}
    </>
  )
}

export default SegmentUpload