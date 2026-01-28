import { useState } from "react"



const SidebarMenu = () => {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(prev => !prev);
  };

  return (
    <>
      <div className="d-flex">
        <nav
          className={`sidebar d-flex flex-column flex-shrink-0 position-fixed ${collapsed ? "collapsed" : ""
            }`}
        >
          <button className="toggle-btn" onClick={toggleSidebar}>
            <i
              className={`fas ${collapsed ? "fa-chevron-right" : "fa-chevron-left"
                }`}
            />
          </button>

          <div className="p-4">
            <h4 className="logo-text fw-bold mb-0">NexusFlow</h4>
            <p className="text-muted small hide-on-collapse">Dashboard</p>
          </div>

          <div className="nav flex-column">
            <a href="#" className="sidebar-link active text-decoration-none p-3">
              <i className="fas fa-home me-3"></i>
              <span className="hide-on-collapse">Dashboard</span>
            </a>

            <a href="#" className="sidebar-link text-decoration-none p-3">
              <i className="fas fa-chart-bar me-3"></i>
              <span className="hide-on-collapse">Analytics</span>
            </a>

            <a href="#" className="sidebar-link text-decoration-none p-3">
              <i className="fas fa-users me-3"></i>
              <span className="hide-on-collapse">Customers</span>
            </a>

            <a href="#" className="sidebar-link text-decoration-none p-3">
              <i className="fas fa-box me-3"></i>
              <span className="hide-on-collapse">Products</span>
            </a>

            <a href="#" className="sidebar-link text-decoration-none p-3">
              <i className="fas fa-gear me-3"></i>
              <span className="hide-on-collapse">Settings</span>
            </a>
          </div>

          <div className="profile-section mt-auto p-4">
            <div className="d-flex align-items-center">
              <img
                src="https://randomuser.me/api/portraits/women/70.jpg"
                alt="Profile"
                className="rounded-circle"
                style={{ height: "60px" }}
              />
              <div className="ms-3 profile-info">
                <h6 className="text-white mb-0">Alex Morgan</h6>
                <small className="text-muted">Admin</small>
              </div>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <div className="container-fluid">
            <h2>Welcome to NexusFlow</h2>
            <p className="text-muted">
              Streamline your workflow with our intuitive dashboard.
            </p>
          </div>
        </main>
      </div>
    </>
  )
}

export default SidebarMenu