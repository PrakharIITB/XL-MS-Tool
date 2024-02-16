import './App.css'
import Process from './pages/process'
import Home from './pages/home'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

function App() {

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Process />} />
          {/* <Route path="/" element={<Home />} /> */}
        </Routes>
      </Router>
    </>
  )
}

export default App
