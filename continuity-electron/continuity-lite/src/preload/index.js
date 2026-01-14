// preload/index.js
// Purpose: secure bridge between renderer and local system (SLM, filesystem, etc)
// Currently unused — will expose explicit APIs when local model integration begins.

import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('api', {
  // future: scanText, loadModel, getScanProgress, etc
})
