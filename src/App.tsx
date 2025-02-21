import { BrowserRouter, Route, Routes } from 'react-router-dom';
// import { LampDemo } from './components/ui/lamp';
import { DashboardPage } from './modules/dashboard/DashboardPage';

// import { FeaturesSectionDemo } from './components/ui/feature';
import { HomePage } from './modules/dashboard/HomePage';

function App() {
  return (

    <BrowserRouter>
      <div className="min-h-screen bg-black-50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/feature" element={<DashboardPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App;

