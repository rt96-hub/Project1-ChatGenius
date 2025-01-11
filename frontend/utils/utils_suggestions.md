# Frontend Utils Suggestions

This document outlines suggestions for improving the utilities in the frontend/utils directory, focusing on code cleanup, simplification, and potential new features.

## API Utility (`api.ts`)

### Current Implementation Analysis

The current implementation is relatively simple and functional, but there are several areas where we can improve robustness, maintainability, and feature set.

### Code Cleanup Suggestions

1. **Token Management**
   - Current Issue: `createAuthenticatedApi` modifies the global api instance's headers
   - Suggestion: Create a new axios instance for authenticated calls to prevent shared state issues
   ```typescript
   export function createAuthenticatedApi(token: string) {
     return axios.create({
       baseURL: API_URL,
       headers: {
         Authorization: `Bearer ${token}`
       }
     });
   }
   ```

2. **Error Handling**
   - Add interceptors for consistent error handling
   - Implement request/response logging in development mode
   ```typescript
   api.interceptors.response.use(
     response => response,
     error => {
       // Consistent error handling
       return Promise.reject(error);
     }
   );
   ```

3. **Type Safety**
   - Add TypeScript interfaces for API responses
   - Create request parameter types
   - Consider generating types from OpenAPI/Swagger specs

### Feature Enhancement Opportunities

1. **Request Queue Management**
   - Implement request debouncing/throttling utilities
   - Add request cancellation support
   ```typescript
   export function createCancellableRequest() {
     const source = axios.CancelToken.source();
     return {
       cancelToken: source.token,
       cancel: () => source.cancel('Request cancelled')
     };
   }
   ```

2. **Caching Layer**
   - Add simple in-memory caching for GET requests
   - Implement cache invalidation strategies
   ```typescript
   const cache = new Map();
   export function getCached(url: string, ttl = 5000) {
     if (cache.has(url)) {
       const { data, timestamp } = cache.get(url);
       if (Date.now() - timestamp < ttl) return data;
     }
     // Proceed with actual request
   }
   ```

3. **Retry Logic**
   - Add configurable retry logic for failed requests
   - Implement exponential backoff
   ```typescript
   export function withRetry(
     request: () => Promise<any>,
     maxRetries = 3,
     delay = 1000
   ) {
     // Implement retry logic
   }
   ```

4. **Request Monitoring**
   - Add request timing metrics
   - Implement request/response logging
   - Create debug utilities for development

### Code Organization Suggestions

1. **Separate Concerns**
   - Move authentication logic to a separate file
   - Create separate utilities for different types of requests (auth, data, etc.)
   - Consider creating a RequestBuilder pattern for complex requests

2. **Configuration Management**
   - Create a separate config file for API-related constants
   - Add environment-specific configurations
   - Implement feature flags support

### Testing Improvements

1. **Test Coverage**
   - Add unit tests for utility functions
   - Create mock interceptors for testing
   - Add integration tests for API utilities

### Documentation Enhancements

1. **Code Documentation**
   - Add JSDoc comments for all exported functions
   - Include examples in documentation
   - Document error handling patterns

### Performance Optimization Areas

1. **Request Optimization**
   - Implement request batching for multiple similar requests
   - Add support for parallel request handling
   - Consider implementing a request queue for large data operations

### Easy Entry Points for New Features

1. **API Response Transformers**
   - Create utility functions for common data transformations
   - Add support for response normalization

2. **Middleware System**
   - Implement a plugin system for request/response middleware
   - Add hooks for request lifecycle events

3. **Development Tools**
   - Create debugging utilities
   - Add request/response logging tools
   - Implement performance monitoring

### Next Steps

Priority order for implementing suggestions:
1. Token management improvement (High Priority)
2. Error handling enhancement (High Priority)
3. Type safety improvements (Medium Priority)
4. Caching layer implementation (Medium Priority)
5. Testing setup (Medium Priority)
6. Documentation updates (Low Priority)
7. Performance optimizations (Low Priority) 