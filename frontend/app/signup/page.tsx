import SignupForm from '@/components/SignupForm'

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h1 className="text-3xl font-bold text-center text-gray-900">ChatGenius</h1>
          <h2 className="mt-6 text-center text-xl text-gray-600">Create your account</h2>
        </div>
        <SignupForm />
      </div>
    </div>
  )
} 