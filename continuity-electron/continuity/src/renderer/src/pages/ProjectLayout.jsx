import { useState } from 'react'
import '@renderer/assets/project-page.css'
import SidebarMenu from '@renderer/components/ProjectLayout/SidebarMenu'
import { Outlet } from 'react-router';


const ProjectLayout = () => {
  const [collapsed, setCollapsed] =useState(false);


  return (
    <>
    <div className={`project-layout ${collapsed ? "sidebar-collapsed" : ""}`}>
      <SidebarMenu collapsed={collapsed} setCollapsed={setCollapsed}/>
      <main className='project-content'>
        <Outlet/>
      </main>
    </div>
    </>
    
  )
}

export default ProjectLayout