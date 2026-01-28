import { Routes, Route, Navigate } from "react-router-dom";
import LaunchPage from "@renderer/pages/LaunchPage";
import SegmentUpload from "@renderer/pages/In-Project-Pages/SegmentUpload"
import ProjectLayout from "./pages/ProjectLayout";
import Dashboard from "@renderer/pages/In-Project-Pages/Dashboard"
import CanonDB from "./pages/In-Project-Pages/CanonDB";


function App() {
  

  return (
    <>
    <Routes>
      {/* Launch - Not in a project yet */}
      <Route path="/" element={<LaunchPage />} />
    
      {/* Now we're in a project */}
        <Route path="/project" element={<ProjectLayout />}>
          {/* default child route */}
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="upload" element={<SegmentUpload />} />
          <Route path="canon" element={<CanonDB />} />
        </Route>
    </Routes>
    </>
  )
}

export default App
