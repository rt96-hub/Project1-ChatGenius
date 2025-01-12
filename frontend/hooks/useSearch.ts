import { useState, useEffect, useCallback } from 'react';

interface UseSearchOptions<T> {
  searchFn: (query: string) => Promise<T>;
  debounceMs?: number;
  minQueryLength?: number;
}

interface UseSearchResult<T> {
  query: string;
  setQuery: (query: string) => void;
  results: T | null;
  isLoading: boolean;
  error: Error | null;
}

export function useSearch<T>({
  searchFn,
  debounceMs = 300,
  minQueryLength = 1,
}: UseSearchOptions<T>): UseSearchResult<T> {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (query.length < minQueryLength) {
      setResults(null);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsLoading(true);
      setError(null);

      try {
        const searchResults = await searchFn(query);
        setResults(searchResults);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Search failed'));
        setResults(null);
      } finally {
        setIsLoading(false);
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [query, searchFn, debounceMs, minQueryLength]);

  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
  };
} 