
import { useEffect, useMemo, useState } from "react";
import projectService from "../../services/projectService";

const API_BASE = "http://localhost:8001";

const emptyForm = {
  name: "",
  type: "concept",
  aliases: "",
  description: "",
  notes: "",
  confidence: "0",
};

const CanonDB = () => {
  const [project, setProject] = useState(null);
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [mergeSourceId, setMergeSourceId] = useState("");
  const [mergeTargetId, setMergeTargetId] = useState("");

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const currentProject = await projectService.loadProject();
        if (!mounted) return;
        setProject(currentProject);
        if (currentProject?.id) {
          await refreshEntities(currentProject.id, "", mounted);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message || "Failed to load Canon data");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, []);

  const refreshEntities = async (projectId, nextQuery = query, mounted = true) => {
    const params = new URLSearchParams();
    if (nextQuery.trim()) params.set("query", nextQuery.trim());
    const res = await fetch(`${API_BASE}/projects/${projectId}/canon/entities${params.toString() ? `?${params.toString()}` : ""}`);
    if (!res.ok) {
      throw new Error(`Failed to load Canon entities (${res.status})`);
    }
    const data = await res.json();
    if (mounted) {
      setEntities(data.entities || []);
    }
  };

  const sortedEntities = useMemo(() => {
    return [...entities].sort((a, b) => (a.name || "").localeCompare(b.name || ""));
  }, [entities]);

  const handleSearch = async (event) => {
    event.preventDefault();
    if (!project?.id) return;
    setLoading(true);
    setError(null);
    try {
      await refreshEntities(project.id, query);
    } catch (err) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!project?.id || !form.name.trim()) return;

    setSaving(true);
    setError(null);

    const payload = {
      name: form.name.trim(),
      type: form.type.trim() || "concept",
      aliases: form.aliases
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean),
      description: form.description.trim() || null,
      notes: form.notes.trim() || null,
      confidence: Number.parseFloat(form.confidence) || 0,
    };

    try {
      const res = await fetch(
        editingId ? `${API_BASE}/entities/${editingId}` : `${API_BASE}/projects/${project.id}/canon/entities`,
        {
          method: editingId ? "PUT" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Save failed (${res.status})`);
      }

      await refreshEntities(project.id);
      setForm(emptyForm);
      setEditingId(null);
    } catch (err) {
      setError(err.message || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (entity) => {
    setEditingId(entity.id);
    setForm({
      name: entity.name || "",
      type: entity.entityType || entity.type || "concept",
      aliases: (entity.aliases || []).join(", "),
      description: entity.description || "",
      notes: entity.notes || "",
      confidence: String(entity.confidence ?? 0),
    });
  };

  const handleDelete = async (entityId) => {
    if (!project?.id) return;
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/entities/${entityId}`, { method: "DELETE" });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Delete failed (${res.status})`);
      }
      await refreshEntities(project.id);
    } catch (err) {
      setError(err.message || "Delete failed");
    } finally {
      setSaving(false);
    }
  };

  const handleMerge = async (event) => {
    event.preventDefault();
    if (!project?.id || !mergeSourceId || !mergeTargetId || mergeSourceId === mergeTargetId) return;

    setSaving(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/projects/${project.id}/canon/entities/merge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_entity_id: mergeSourceId, target_entity_id: mergeTargetId }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Merge failed (${res.status})`);
      }
      await refreshEntities(project.id);
      setMergeSourceId("");
      setMergeTargetId("");
    } catch (err) {
      setError(err.message || "Merge failed");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="canon-db">Loading Canon Database…</div>;
  }

  if (!project?.id) {
    return (
      <div className="canon-db">
        <h2>Canon Database</h2>
        <p>No active project is selected yet.</p>
      </div>
    );
  }

  return (
    <div className="canon-db" style={{ padding: "1.5rem", display: "grid", gap: "1.25rem" }}>
      <div>
        <h2 style={{ marginBottom: "0.25rem" }}>Canon Database</h2>
        <p style={{ margin: 0, opacity: 0.8 }}>Project: {project.name || project.id}</p>
      </div>

      {error && <div style={{ padding: "0.75rem", background: "#3a1d1d", color: "#ffd7d7", borderRadius: "8px" }}>{error}</div>}

      <form onSubmit={handleSearch} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search Canon entities"
          style={{ minWidth: "260px", flex: "1" }}
        />
        <button type="submit" disabled={loading || saving}>Search</button>
      </form>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "0.75rem", padding: "1rem", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "12px" }}>
        <strong>{editingId ? "Edit Entity" : "Create Entity"}</strong>
        <div style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
          <input required type="text" value={form.name} onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))} placeholder="Name" />
          <input type="text" value={form.type} onChange={(event) => setForm((prev) => ({ ...prev, type: event.target.value }))} placeholder="Type" />
          <input type="text" value={form.confidence} onChange={(event) => setForm((prev) => ({ ...prev, confidence: event.target.value }))} placeholder="Confidence" />
        </div>
        <input type="text" value={form.aliases} onChange={(event) => setForm((prev) => ({ ...prev, aliases: event.target.value }))} placeholder="Aliases, comma separated" />
        <textarea value={form.description} onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))} placeholder="Description" rows={3} />
        <textarea value={form.notes} onChange={(event) => setForm((prev) => ({ ...prev, notes: event.target.value }))} placeholder="Notes" rows={3} />
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button type="submit" disabled={saving}>{editingId ? "Save Changes" : "Create Entity"}</button>
          {editingId && (
            <button type="button" onClick={() => { setEditingId(null); setForm(emptyForm); }} disabled={saving}>
              Cancel Edit
            </button>
          )}
        </div>
      </form>

      <form onSubmit={handleMerge} style={{ display: "grid", gap: "0.75rem", padding: "1rem", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "12px" }}>
        <strong>Merge Entities</strong>
        <div style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
          <select value={mergeSourceId} onChange={(event) => setMergeSourceId(event.target.value)}>
            <option value="">Source entity</option>
            {sortedEntities.map((entity) => (
              <option key={entity.id} value={entity.id}>{entity.name}</option>
            ))}
          </select>
          <select value={mergeTargetId} onChange={(event) => setMergeTargetId(event.target.value)}>
            <option value="">Target entity</option>
            {sortedEntities.map((entity) => (
              <option key={entity.id} value={entity.id}>{entity.name}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={saving || !mergeSourceId || !mergeTargetId || mergeSourceId === mergeTargetId}>Merge</button>
      </form>

      <div style={{ display: "grid", gap: "0.75rem" }}>
        {sortedEntities.length === 0 ? (
          <p>No Canon entities found.</p>
        ) : (
          sortedEntities.map((entity) => (
            <div key={entity.id} style={{ padding: "1rem", border: "1px solid rgba(255,255,255,0.12)", borderRadius: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap" }}>
                <div>
                  <strong>{entity.name}</strong> <span style={{ opacity: 0.75 }}>({entity.entityType || entity.type || "concept"})</span>
                  <div style={{ opacity: 0.75, marginTop: "0.25rem" }}>
                    ID: {entity.id} · Version: {entity.version || 1} · Status: {entity.status || "active"} · Sync: {entity.sync_status || "pending"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  <button type="button" onClick={() => handleEdit(entity)} disabled={saving}>Edit</button>
                  <button type="button" onClick={() => handleDelete(entity.id)} disabled={saving}>Delete</button>
                </div>
              </div>
              {entity.aliases?.length ? <div style={{ marginTop: "0.5rem" }}>Aliases: {entity.aliases.join(", ")}</div> : null}
              {entity.description ? <div style={{ marginTop: "0.25rem" }}>{entity.description}</div> : null}
              {entity.notes ? <div style={{ marginTop: "0.25rem", opacity: 0.8 }}>{entity.notes}</div> : null}
              <div style={{ marginTop: "0.5rem", opacity: 0.75 }}>
                Facts: {Array.isArray(entity.facts) ? entity.facts.length : 0} · Stories: {entity.story_ids?.length || 0}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default CanonDB