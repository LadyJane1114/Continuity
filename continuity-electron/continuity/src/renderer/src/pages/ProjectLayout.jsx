import { useState, useEffect } from 'react'
import '@renderer/assets/project-page.css'
import SidebarMenu from '@renderer/components/ProjectLayout/SidebarMenu'
import { Outlet } from "react-router-dom";


const ProjectLayout = () => {
  const [collapsed, setCollapsed] =useState(true);
  useEffect(() => {
    document.body.style.overflow = collapsed ? "" : "hidden";
  }, [collapsed]);



  return (

    <div className={`project-layout`}>
      <SidebarMenu collapsed={collapsed} setCollapsed={setCollapsed} />
      <main className='project-content'>
        <Outlet />
      </main>
    </div>

    
  )
}

export default ProjectLayout