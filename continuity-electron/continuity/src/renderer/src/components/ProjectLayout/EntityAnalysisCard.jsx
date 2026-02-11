


const EntityAnalysisCard = ({ entities = [], facts = [], editable = false, onAccept, onReject }) => {
  return (
    <div className="entity-card">
        <h3>Entity</h3>
        <div className="entity-row">
            {entities.map((e)=> (
                <span key={e} className="entity-chip">{e}</span>
            ))}
        </div>

        <h3>Facts</h3>
        <ul className="fact-list">
            {facts.map((fact, i) => (
          <li key={i} className={`fact fact-${fact.accepted}`}>
            {fact.text}

            {editable && (
              <span className="fact-actions">
                <button onClick={() => onAccept(i)}>Accept</button>
                <button onClick={() => onReject(i)}>Reject</button>
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