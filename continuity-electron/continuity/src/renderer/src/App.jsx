import { Routes, Route, Navigate } from "react-router-dom";
import LaunchPage from "@renderer/pages/LaunchPage";
import SegmentUpload from "@renderer/pages/In-Project-Pages/SegmentUpload"
import ProjectLayout from "./pages/ProjectLayout";
import Dashboard from "@renderer/pages/In-Project-Pages/Dashboard"
import CanonDB from "./pages/In-Project-Pages/CanonDB";
import Settings from "./pages/In-Project-Pages/Settings";
import StorySegments from "./pages/In-Project-Pages/StorySegments";


function App() {
  

  return (
    <>
    <Routes>
      {/* Launch - Not in a project yet */}
      <Route path="/" element={<LaunchPage />} />
    
      {/* Now we're in a project */}
        <Route path="/project" element={<ProjectLayout />}>
          {/* default child route */}
          <Route index element={<Navigate to="cont-dashboard" replace />} />
          <Route path="cont-dashboard" element={<Dashboard />} />
          <Route path="segment-upload" element={<SegmentUpload />} />
          <Route path="story-segments" element={<StorySegments/>}/>
          <Route path="canon-db" element={<CanonDB />} />
          <Route path="cont-settings" element={<Settings />} />
        </Route>
    </Routes>
    </>
  )
}

export default App
