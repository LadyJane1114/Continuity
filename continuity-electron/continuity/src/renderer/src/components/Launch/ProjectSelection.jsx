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
            {/* technically this button shouldn't just navigate to the project it should allow you to name the project and then when you name it, it'll take you to the project page, but for right now it's just taking you to the project page for the sake of time. */}
            <div className='card-button'>
                <button className="CreateBtn" onClick={() => navigate("/project")}>
                    Create
                </button>
            </div>
            
        </div>
    </div>
    {/* this button is for later when we have the ability to have multiple project, but right now we don't, so I'm just saving it for later. (it's also nto even really the way I would do the button, I just want to remember that I want it to exist. The code for this would look more like the above, but the buttons would look slightly different (CSS available in launch-page.css)) */}
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