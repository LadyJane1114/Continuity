import React from 'react'

const TestModal = ({message, onClose}) => {
  return (
    <>
    <div className='modal-overlay'>
        <div className='modal-content'>
            <p>{message}</p>
            <button onClick={onClose}>Okay</button>
        </div>
    </div>
    </>
  )
}

export default TestModal