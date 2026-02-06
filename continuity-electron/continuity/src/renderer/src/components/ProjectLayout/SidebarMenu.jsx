
import { NavLink } from "react-router-dom";
import { FiChevronLeft, FiChevronRight, FiHome, FiSettings } from 'react-icons/fi';
import { FaRegPenToSquare } from "react-icons/fa6";
import { GiPirateCannon,GiExitDoor } from "react-icons/gi";


const SidebarMenu = ({ collapsed, setCollapsed }) => {
  const toggleSidebar = () => setCollapsed(prev => !prev);
  const handleExit = () => {
    window.api.quitApp();
  };

  return (
    <>
      {!collapsed && (
        <div
          className="sidebar-overlay"
          onClick={() => setCollapsed(true)}
        />
      )}
      
        <nav className={`sidebar ${collapsed ? "collapsed" : ""}`}>
          <button className="toggle-btn" onClick={toggleSidebar}>
            {collapsed ? <FiChevronRight size={20} color="#000000" /> : <FiChevronLeft size={20} color="#000000" />}
          </button>

          <div className="p-4">
            <img className="sidebar-logo" src="../../resources/LogoWSplash.png" alt="Continuity Logo" />
          </div>

          <div className="nav-links">
            <NavLink to="cont-dashboard" className="sidebar-link">
              <FiHome className="sidebar-icon"/> <span className="hide-on-collapse">Dashboard</span>
            </NavLink>
            <NavLink to="segment-upload" className="sidebar-link">
              <FaRegPenToSquare className="sidebar-icon" /><span className="hide-on-collapse">Upload a Segment</span>
            </NavLink>
            <NavLink to="canon-db" className="sidebar-link">
              <GiPirateCannon className="sidebar-icon" /><span className="hide-on-collapse">Canon Database</span>
            </NavLink>
            <NavLink to="cont-settings" className="sidebar-link">
              <FiSettings className="sidebar-icon" /><span className="hide-on-collapse">Settings</span>
            </NavLink>
            <button className="sidebar-link" onClick={handleExit}>
              <GiExitDoor className="sidebar-icon"/><span className="hide-on-collapse">Exit</span>
            </button>
          </div>
        </nav>
    </>
  )
}

export default SidebarMenu