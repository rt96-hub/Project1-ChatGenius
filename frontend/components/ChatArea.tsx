import { PaperAirplaneIcon } from '@heroicons/react/24/solid'

export default function ChatArea() {
  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Example messages - these will be replaced with real data */}
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-gray-300" />
          <div>
            <div className="flex items-baseline gap-2">
              <span className="font-medium">John Doe</span>
              <span className="text-xs text-gray-500">12:34 PM</span>
            </div>
            <p className="text-gray-800">Hello team! How is everyone doing today?</p>
          </div>
        </div>
      </div>
      
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Type a message..."
            className="flex-1 rounded-lg border border-gray-200 px-4 py-2 focus:outline-none focus:border-blue-500"
          />
          <button className="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600">
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
} 