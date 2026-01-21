import { Routes, Route } from "react-router-dom";
import LaunchPage from "./pages/LaunchPage";
import ProjectPage from "./pages/ProjectPage";


function App() {
  

  return (
    <>
    <Routes>
      <Route path="/" element={<LaunchPage/>}/>
      <Route path="/project" element={<ProjectPage />} />
    </Routes>
    </>
  )
}

export default App
