import { useAuth } from '@/hooks/useAuth';

export function AuthButton() {
  const { isAuthenticated, isLoading, login, signOut, user } = useAuth();

  if (isLoading) {
    return <button className="px-4 py-2 bg-gray-200 rounded" disabled>Loading...</button>;
  }

  if (isAuthenticated) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm">{user?.email}</span>
        <button
          onClick={() => signOut()}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => login()}
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
    >
      Login
    </button>
  );
} 