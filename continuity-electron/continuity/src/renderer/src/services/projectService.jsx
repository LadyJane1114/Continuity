const STORAGE_KEY="currentProject"

const projectService = {
  async createProject(name) {
    const project = {
        id: crypto.randomUUID(),
        name,
        createdAt: new Date().toISOString(),
        lastOpened: new Date().toISOString(),
        recentActivity:[]
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(project))
    return project;
  },

  async loadProject() {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : null;
  },

  async saveProject(project) {
    project.lastOpened = new Date().toISOString();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(project))
  },

  async clearProject() {
    localStorage.removeItem(STORAGE_KEY)
  }
}

export default projectService