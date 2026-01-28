import { useState } from "react"



const SidebarMenu = () => {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(prev => !prev);
  };

  return (
    <>
    <div className="d-flex">
        <nav className={`sidebar d-flex flex-column flex-shrink-0 position-fixed ${collapsed ? "collapsed" : ""
          }`}>
            <button className="toggle-btn" onClick={toggleSidebar}>

            </button>
            <div className="p-4">
              <h4 className="logo-text fw-bold mb-0">Menu</h4>
              <p className="text-muted small hide-on-collapse">Menu</p>
            </div>
          </nav>
    </div>
    </>
  )
}

export default SidebarMenu