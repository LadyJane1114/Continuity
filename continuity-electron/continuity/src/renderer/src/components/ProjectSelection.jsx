import React from 'react'

const ProjectSelection = () => {
  return (
    <>
    <div className='card'>
        <div className='card-body'>
            <h3>Create a new Project</h3>
            <p>Create a new Continuity project with a new body of work.</p>
            <a href='#' className='CreateBtn'>Create</a>
        </div>
    </div>
    <div className='card'>
        <div className='card-body'>
            <h3>Open an Existing Project</h3>
            <a href='#' className='LoadBtn'>Load</a>
        </div>
    </div>
    </>
  )
}

export default ProjectSelection