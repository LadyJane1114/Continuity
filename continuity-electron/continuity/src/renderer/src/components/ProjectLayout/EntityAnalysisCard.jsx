


const EntityAnalysisCard = ({ entity, editable = false, onAccept, onReject }) => {
  return (
    <div className="entity-card">
        <h3>{entity.name}</h3>
        <div>Type: {entity.type}</div>
        <div>Aliases: {entity.aliases.length > 0 ? entity.aliases.join(","): "None"}</div>

        <h3>Facts</h3>
        <ul className="fact-list">
          {entity.facts.map((fact) => (
            <li key={fact.id} className={`fact fact-${fact.accepted}`}>
              {fact.text}

              {editable && (
                <span className="fact-actions">
                  <button onClick={() => onAccept(entity.id, fact.id)}>Accept</button>
                  <button onClick={() => onReject(entity.id, fact.id)}>Reject</button>
                </span>
              )}

              {!editable && (
                <span className="fact-status">
                  {fact.accepted === true && "✓ accepted"}
                  {fact.accepted === false && "✕ rejected"}
                  {fact.accepted === null && "• undecided"}
                </span>
              )}
            </li>
          ))}
        </ul>

    </div>
  )
}

export default EntityAnalysisCard