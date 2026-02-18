import { useEffect, useState } from "react";
import Hero from '../../components/ProjectLayout/Dashboard/Hero'
import InfoCards from '../../components/ProjectLayout/Dashboard/InfoCards'
import projectService from "../../services/projectService";

const Dashboard = () => {
  const [project,setProject] = useState(null)

  useEffect(()=> {
    const loadProject = async () => {
      const p = await projectService.loadProject();
      setProject(p);
    }
    loadProject();
  },[])

  if(!project) return <p>Loading project...</p>

  return (
    <div className='cont-dashboard'>
      <Hero project={project}/>
      <InfoCards project={project}/>
    </div>
  )
}

export default Dashboard