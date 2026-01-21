import React from 'react'
import {Link, useNavigate} from "react-router-dom"

const ProjectSelection = () => {
    const navigate = useNavigate();

  return (
    <>
    <div className='card'>
        <div className='card-body'>
            <div className='card-text'>
                <h3>Create a new Project</h3>
                <p>Create a new Continuity project with a new body of work.</p>
            </div>
            <div className='card-button'>
                <button className="CreateBtn" onClick={() => navigate("/project")}>
                    Create
                </button>
            </div>
            
        </div>
    </div>
    {/* <div className='card'>
        <div className='card-body'>
            <h3>Open an Existing Project</h3>
            <a href='#' className='LoadBtn'>Load</a>
        </div>
    </div> */}
    </>
  )
}

export default ProjectSelection