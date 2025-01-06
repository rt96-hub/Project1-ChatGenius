import Header from '@/components/Header'
import Sidebar from '@/components/Sidebar'
import ChatArea from '@/components/ChatArea'

export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <ChatArea />
      </div>
    </div>
  )
}

