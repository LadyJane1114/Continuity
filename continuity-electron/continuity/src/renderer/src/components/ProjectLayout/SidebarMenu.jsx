import { useState } from "react"
import { NavLink } from "react-router";
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi';





const SidebarMenu = () => {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(prev => !prev);
  };

  return (
    <>
      <div className="d-flex">
        <nav className={`sidebar d-flex flex-column flex-shrink-0 position-fixed ${collapsed ? "collapsed" : ""}`}>
          <button className="toggle-btn" onClick={toggleSidebar}>
            {collapsed ? <FiChevronRight size={20} color="#000000" /> : <FiChevronLeft size={20} color="#000000" />}
          </button>

          <div className="p-4">
            <h3 className="logo-text">Continuity</h3>
            <p className="text-muted hide-on-collapse">Menu</p>
          </div>

          <div className="nav-links">
            <NavLink path="dashboard">Home</NavLink>
            <NavLink path="upload">Upload a Segment</NavLink>
            <NavLink path="canon">My Story Database</NavLink>
          </div>
        </nav>
      </div>
    </>
  )
}

export default SidebarMenu