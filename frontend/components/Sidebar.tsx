import { HashtagIcon, UserGroupIcon } from '@heroicons/react/24/outline'

export default function Sidebar() {
  return (
    <aside className="w-64 min-w-[16rem] bg-gray-800 text-white flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-xl font-bold">Workspace</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 mb-6 mt-4">
          <h3 className="text-gray-400 text-sm font-medium mb-2 uppercase tracking-wide">Channels</h3>
          <ul className="space-y-1">
            {['general', 'random', 'announcements'].map((channel) => (
              <li key={channel}>
                <button className="flex items-center gap-2 w-full px-2 py-1.5 rounded hover:bg-gray-700 transition-colors">
                  <HashtagIcon className="h-4 w-4" />
                  <span className="truncate">{channel}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="px-4">
          <h3 className="text-gray-400 text-sm font-medium mb-2 uppercase tracking-wide">Direct Messages</h3>
          <ul className="space-y-1">
            {['John Doe', 'Jane Smith', 'Team Lead'].map((user) => (
              <li key={user}>
                <button className="flex items-center gap-2 w-full px-2 py-1.5 rounded hover:bg-gray-700 transition-colors">
                  <UserGroupIcon className="h-4 w-4" />
                  <span className="truncate">{user}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </aside>
  )
} 