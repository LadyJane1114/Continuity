import '@renderer/assets/launch-page.css'
import Branding from '@renderer/components/Launch/Branding'
import ProjectSelection from '@renderer/components/Launch/ProjectSelection'

const LaunchPage = () => {
  return (
    <div className='launch-page'>
    <Branding/>
    <ProjectSelection/>
    </div>
  )
}

export default LaunchPage