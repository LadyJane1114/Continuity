import { useEffect, useState } from "react";
import {useNavigate} from "react-router-dom"
import projectService from "../../services/projectService";

const ProjectSelection = () => {
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [projectName, setProjectName] = useState("")
    const [isCreating, setIsCreating] = useState(false)

    useEffect(()=> {
        const checkProject = async ()=> {
            const existing = await projectService.loadProject();
            setProject(existing);
        }
        checkProject();
    }, [])

    const handleCreateStart = () => {
        setIsCreating(true);
    }

    const handleCreateConfirm = async ()=> {
        if(!projectName.trim()) return;
        
        await projectService.createProject(projectName);
        navigate("/project");
    }

    const handleLoad = () => {
        navigate("/project");
    }

    const handleRemoveProject = async () =>{
        const RUSure = window.confirm("Are you sure you want to remove this project? This action cannot be undone.");
        if(!RUSure)return;

        await projectService.clearProject();
        setProject(null);
        setIsCreating(false);
        setProjectName("");
    }

  return (
    <>
    <div className='card'>
        <div className='card-body'>
            <div className='card-text'>
                {project ? (
                    <>
                    <h3>Load Existing Project</h3>
                    <p>{project.name}</p>
                    </>
                ):(
                    <>
                    <h3>Create a new Project</h3>
                    <p>Create a new Continuity project with a new body of work.</p>
                    </>
                    
                )}
            </div>

            <div className='card-button'>
                {project ? (
                    <button className="LoadBtn" onClick={handleLoad}>Load Project</button>
                ):(
                    !isCreating ? (
                        <button className="CreateBtn" onClick={handleCreateStart}>Create New Project</button>
                    ):(
                        <>
                        <input className="progNameInput" type="text" value={projectName} onChange={(e)=>setProjectName(e.target.value)} placeholder="Enter Project Name"/>
                        <button className="CreateBtn" onClick={handleCreateConfirm}>Confirm Project Name</button>
                        </>
                    )
                )}
                {project && (
                    <button className="DeleteBtn" onClick={handleRemoveProject}>Delete Project</button>
                )}
            </div>
        </div>
    </div>
    </>
  )
}

export default ProjectSelection