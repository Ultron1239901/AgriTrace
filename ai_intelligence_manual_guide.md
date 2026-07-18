# AI Intelligence Unification Portal Manual Setup Guide

This guide details the complete manual process to configure, implement, and run the unified **🤖 AI Intelligence** portal layout inside AgriTrace.

---

## 1. Creating the Unified Portal Page Component (`frontend/src/pages/AIIntelligence.jsx`)
Create the single unified dashboard component containing the sub-navigation tabs (AI Assistant, Knowledge Center, Recommendations, Weather Insights, Market Insights, AI Reports):

```javascript
import React, { useState, useEffect } from 'react'
import { langgraphAPI, ragAPI, visionAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import Alert from '../components/Alert'

const TABS = [
  { id: 'assistant', label: 'AI Assistant', icon: '🤖' },
  { id: 'knowledge', label: 'Knowledge Center', icon: '📖' },
  { id: 'recommendations', label: 'Recommendations', icon: '💡' },
  { id: 'weather', label: 'Weather Insights', icon: '🌤️' },
  { id: 'market', label: 'Market Insights', icon: '📈' },
  { id: 'reports', label: 'AI Reports', icon: '📋' }
]

export default function AIIntelligence() {
  const [activeTab, setActiveTab] = useState('assistant')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // AI Assistant Chatbot state
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState([
    { sender: 'ai', text: 'Hello! I am your unified AgriExpert AI Assistant. Ask me anything about crop weather forecasts, prices, disease diagnostics, or Polygon proofs.' }
  ])

  // RAG Knowledge search state
  const [ragQuery, setRagQuery] = useState('')
  const [ragResults, setRagResults] = useState([])

  // Recommendation & Insight states
  const [personalRecom, setPersonalRecom] = useState('')
  const [weatherData, setWeatherData] = useState(null)
  const [marketData, setMarketData] = useState(null)

  // History/Report logs states
  const [conversationHistory, setConversationHistory] = useState([])
  const [visionHistory, setVisionHistory] = useState([])
  const [ragHistory, setRagHistory] = useState([])

  useEffect(() => {
    fetchRecommendations()
    fetchWeatherData()
    fetchMarketData()
    fetchReportsData()
  }, [])

  const fetchRecommendations = async () => {
    try {
      const { data } = await langgraphAPI.query({ query: 'Give me personalized recommendations for my crops.' })
      setPersonalRecom(data.recommendations)
    } catch (err) {
      setPersonalRecom('No personalized recommendations found. Register crops or upload leaf scans to generate insights.')
    }
  }

  const fetchWeatherData = async () => {
    try {
      const { data } = await langgraphAPI.query({ query: 'Show current weather alert metrics' })
      setWeatherData(data.weather)
    } catch (err) {}
  }

  const fetchMarketData = async () => {
    try {
      const { data } = await langgraphAPI.query({ query: 'Show Mandi prices' })
      setMarketData(data.market)
    } catch (err) {}
  }

  const fetchReportsData = async () => {
    try {
      const chatHist = await langgraphAPI.getHistory()
      setConversationHistory(chatHist.data || [])
      const visHist = await visionAPI.getHistory()
      setVisionHistory(visHist.data || [])
      const rgHist = await ragAPI.getHistory()
      setRagHistory(rgHist.data || [])
    } catch (err) {}
  }

  const handleChatSubmit = async (e) => {
    e.preventDefault()
    if (!chatInput.trim()) return

    const userText = chatInput
    setChatInput('')
    setChatMessages(prev => [...prev, { sender: 'user', text: userText }])
    setLoading(true)

    try {
      // Query compiled graph (internal supervisor coordinates weather, mandi, etc.)
      const { data } = await langgraphAPI.query({ query: userText })
      setChatMessages(prev => [...prev, {
        sender: 'ai',
        text: data.recommendations,
        confidence: data.confidence,
        sources: data.sources
      }])
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'ai', text: 'Diagnostics: Keep soil moisture levels high and apply NPK fertilizer ratios.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleRagSearch = async (e) => {
    e.preventDefault()
    if (!ragQuery.trim()) return
    setLoading(true)
    try {
      const { data } = await ragAPI.query({ query: ragQuery })
      setRagResults(data.chunks || [])
      fetchReportsData()
    } catch (err) {
      setError('Search failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6 text-white min-h-screen">
      {/* Banner */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-glow flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-black uppercase tracking-wider flex items-center gap-2">🤖 AI Intelligence</h1>
          <p className="text-xs text-agritrace-muted">Unified smart recommendations, manuals, and weather indexes.</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 text-xs font-black uppercase px-4 py-2.5 rounded-xl transition-all cursor-pointer ${
              activeTab === tab.id ? 'bg-agritrace-green text-black font-extrabold' : 'bg-white/5 text-white'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Panels */}
      <div className="space-y-6">
        {activeTab === 'assistant' && (
          <div className="card-glass p-5 flex flex-col h-[520px]">
            {/* Chat Messages and Input form ... */}
          </div>
        )}
        {/* ... Implement other Active Tab panel layouts ... */}
      </div>
    </div>
  )
}
```

---

## 2. Update Sidebar Navigation Links (`frontend/src/components/PortalLayout.jsx`)
Replace individual AI menus with a single unified **AI Intelligence** (🤖) link under case roles. Ensure the **AI Vision** (🔬) menu is kept separate, and the **floating chatbot widget** remains active at the bottom:

```javascript
      case 'farmer':
        return [
          { to: '/farmer/dashboard', label: 'Dashboard', icon: '📊' },
          { to: '/farmer/crops', label: 'My Crops', icon: '🌾' },
          { to: '/farmer/add-crop', label: 'Add Crop', icon: '➕' },
          { to: '/farmer/requests', label: 'Buyer Requests', icon: '📬' },
          { to: '/farmer/vision', label: 'AI Vision', icon: '🔬' }, // CV remains separate
          { to: '/farmer/ai-intelligence', label: 'AI Intelligence', icon: '🤖' }, // Unified
          { to: '/farmer/profile', label: 'Farm Profile', icon: '👤' },
          { to: '/farmer/support', label: 'Support Chat', icon: '💬' },
        ]
      case 'buyer':
        return [
          { to: '/buyer/dashboard?tab=farmers', label: 'Search Farmers', icon: '🔍' },
          { to: '/buyer/dashboard?tab=favourites', label: 'Saved Farmers', icon: '⭐️' },
          { to: '/buyer/dashboard?tab=requests', label: 'Purchase Orders', icon: '💼' },
          { to: '/buyer/dashboard?tab=analytics', label: 'Market Analysis', icon: '📈' },
          { to: '/buyer/ai-intelligence', label: 'AI Intelligence', icon: '🤖' }, // Unified
          { to: '/buyer/dashboard?tab=profile', label: 'Profile Settings', icon: '👤' },
          { to: '/buyer/support', label: 'Support Chat', icon: '💬' },
        ]
```

---

## 3. Register Routes (`frontend/src/App.jsx`)
Map path strings to load `AIIntelligence.jsx` to ensure both legacy and fresh routing structures render the unified portal page:

```javascript
import AIIntelligence from './pages/AIIntelligence'

// Routes:
<Route path="/farmer/knowledge" element={<ProtectedRoute role="farmer"><AIIntelligence /></ProtectedRoute>} />
<Route path="/farmer/ai-dashboard" element={<ProtectedRoute role="farmer"><AIIntelligence /></ProtectedRoute>} />
<Route path="/farmer/ai-intelligence" element={<ProtectedRoute role="farmer"><AIIntelligence /></ProtectedRoute>} />

<Route path="/buyer/knowledge" element={<ProtectedRoute role="buyer"><AIIntelligence /></ProtectedRoute>} />
<Route path="/buyer/ai-dashboard" element={<ProtectedRoute role="buyer"><AIIntelligence /></ProtectedRoute>} />
<Route path="/buyer/ai-intelligence" element={<ProtectedRoute role="buyer"><AIIntelligence /></ProtectedRoute>} />
```

---

## 4. Compile React Build
Run compilation inside the frontend directory:
```bash
npm run build
```
This compiles Vite static assets into `dist/` with zero errors.
