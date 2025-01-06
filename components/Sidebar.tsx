import React from 'react'

const Sidebar = () => {
  return (
    <aside className="bg-purple-800 text-purple-100 w-64 flex-shrink-0 overflow-y-auto">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Channels</h2>
        <ul className="space-y-2">
          <li className="hover:bg-purple-700 px-2 py-1 rounded"># general</li>
          <li className="hover:bg-purple-700 px-2 py-1 rounded"># random</li>
        </ul>
      </div>
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Direct Messages</h2>
        <ul className="space-y-2">
          <li className="hover:bg-purple-700 px-2 py-1 rounded">John Doe</li>
          <li className="hover:bg-purple-700 px-2 py-1 rounded">Jane Smith</li>
        </ul>
      </div>
    </aside>
  )
}

export default Sidebar

