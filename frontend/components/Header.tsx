'use client'

import { Bars3Icon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { useAuth } from '@/contexts/AuthContext'

export default function Header() {
  const { logout } = useAuth()

  return (
    <header className="h-14 min-h-[3.5rem] border-b border-gray-200 bg-white flex items-center px-4 justify-between shadow-sm">
      <div className="flex items-center gap-4">
        <button className="md:hidden p-1 hover:bg-gray-100 rounded">
          <Bars3Icon className="h-6 w-6 text-gray-500" />
        </button>
        <h1 className="text-xl font-semibold text-gray-800">ChatGenius</h1>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="relative">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search messages..."
            className="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={logout}
          className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
        >
          Sign out
        </button>
      </div>
    </header>
  )
} 