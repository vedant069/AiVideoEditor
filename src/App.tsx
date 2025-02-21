import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { LampDemo } from './components/ui/lamp';
import { DashboardPage } from './modules/dashboard/DashboardPage';

function App() {
  return (

    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<LampDemo />} />
          <Route path="/feature" element={<DashboardPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App;