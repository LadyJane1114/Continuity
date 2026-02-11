import { useState } from "react"


const StorySegments = () => {
  const [openId, setOpenId] = useState(null);

  const toggleCard = (id) => {
    setOpenId(prev => (prev=== id ? null : id));
  }

  return (
    <div className='story-segments'>
      <h1>My Story Segments</h1>
      {/* Experimental */}
      <div className='segment-card' onClick={() => toggleCard(1)} style={{ cursor: "pointer" }}>
        <div className='segment-card-header' >
          {/* <h3>{title}</h3> */}
          <h2>Chapter 1    {openId === 1 ? "▼" : "▶"}</h2>
        </div>
        <div className='segment-card-body'>
          {/* <p>{summary}</p> */}
          <p>Tara meets Rodney on the way to her grandmother's house. On the train, they have to hide from the ticket inspector, because they realize both of their tickets are invalid.</p>
        </div>

        <div className={`accordion-body ${openId === 1 ? "open" : ""}`}>
          {/* <p>{details}</p> */}
          <p>ALL THE OTHER INFO WOULD GO IN HERE, AND BE ACTUALLY FORMATTED CORRECTLY, BUT I'M JUST TRYING TO SEE IF THIS WORKS RIGHT NOW</p>
        </div>

      </div>

      <div className='segment-card' onClick={() => toggleCard(2)} style={{ cursor: "pointer" }}>
        <div className='segment-card-header' >
          {/* <h3>{title}</h3> */}
          <h2>Chapter 2   {openId === 2 ? "▼" : "▶"}</h2>
        </div>
        <div className='segment-card-body'>
          {/* <p>{summary}</p> */}
          <p>Blah blah blah blah I am the summary of a story segment. I am one to two sentences long and I summarize the things that are in this segment.</p>
        </div>

        <div className={`accordion-body ${openId === 2 ? "open" : ""}`}>
          {/* <p>{details}</p> */}
          <p>ALL THE OTHER INFO WOULD GO IN HERE, AND BE ACTUALLY FORMATTED CORRECTLY, BUT I'M JUST TRYING TO SEE IF THIS WORKS RIGHT NOW</p>
        </div>

      </div>

    </div>
  )
}

export default StorySegments