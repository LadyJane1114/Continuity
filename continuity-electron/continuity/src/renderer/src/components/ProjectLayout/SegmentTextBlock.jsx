

const SegmentTextBlock = ({segment}) => {
  return (
    <pre style={{
      whiteSpace: 'pre-wrap',
      wordWrap: 'break-word',
      overflowY: 'auto',
      padding: '1rem',
      borderRadius: '6px',
      fontFamily: 'monospace',
      margin: 0, 
      minHeight: '10em',
    }}>
      <code>{segment}</code>
    </pre>
  )
}

export default SegmentTextBlock