import { useState } from "react"
import { NavLink } from "react-router-dom";
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi';





const SidebarMenu = () => {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(prev => !prev);
  };

  return (
    <>
    
      <div>
        <nav className={`sidebar ${collapsed ? "collapsed" : ""}`}>
          <button className="toggle-btn" onClick={toggleSidebar}>
            {collapsed ? <FiChevronRight size={20} color="#000000" /> : <FiChevronLeft size={20} color="#000000" />}
          </button>

          <div className="p-4">
            <h3 className="logo-text">Continuity</h3>
            <p className="text-muted hide-on-collapse">Menu</p>
          </div>

          <div className="nav-links">
            <NavLink to="cont-dashboard">Home</NavLink>
            <NavLink to="segment-upload">Upload a Segment</NavLink>
            <NavLink to="canon-db">My Story Database</NavLink>
          </div>
        </nav>
      </div>
    </>
  )
}

export default SidebarMenu