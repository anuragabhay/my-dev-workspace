import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Generate } from '@/pages/Generate'
import { History } from '@/pages/History'
import { ExecutionDetail } from '@/pages/ExecutionDetail'
import { Config } from '@/pages/Config'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="generate" element={<Generate />} />
          <Route path="history" element={<History />} />
          <Route path="execution/:id" element={<ExecutionDetail />} />
          <Route path="config" element={<Config />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
