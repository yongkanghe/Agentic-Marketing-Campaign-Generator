# ADR-017: Frontend-Backend API Data Transformation Strategy

**Date**: 2025-06-24
**Status**: Superseded by [ADR-018](./ADR-018-Backend-CamelCase-API-Contract.md)
**Author**: JP

## Superseded Reason

This ADR proposed a frontend-based transformation layer to handle `snake_case` from the backend and `camelCase` in the frontend. While this approach seemed logical, the implementation proved to be complex and error-prone. The key transformation logic led to several critical runtime errors, particularly with `null` or `undefined` values in API responses, and created a fragile data contract that was difficult to debug.

The new strategy, documented in **ADR-018**, moves the responsibility of data formatting to the backend. The backend API will now serve `camelCase` JSON directly, eliminating the need for any transformation on the frontend. This creates a simpler, more robust, and more maintainable architecture.

---

## Original ADR Content (For Historical Reference)

### Context

The application consists of a Python/FastAPI backend and a React/TypeScript frontend. A critical and recurring source of bugs has been the mismatch in data object conventions between the two environments:
-   **Backend (Python)**: Follows `snake_case` convention for object keys (e.g., `image_url`).
-   **Frontend (TypeScript)**: Follows `camelCase` convention for object properties (e.g., `imageUrl`).

This inconsistency has led to silent failures where data fetched from the backend was not correctly mapped to the frontend state, resulting in missing images, videos, and other critical information in the UI.

## Problem

The lack of a formal data transformation strategy caused several issues:

1.  **Silent Failures**: When the backend returned `{"image_url": "..."}` and the frontend expected `{"imageUrl": "..."}`, the data was simply ignored without error, leading to a degraded user experience (e.g., showing placeholders instead of real content).
2.  **Inconsistent Transformations**: Manual, ad-hoc transformations were scattered across different frontend components, leading to bugs and making the code difficult to maintain.
3.  **Increased Debugging Time**: A significant amount of development time was spent tracing these data mapping issues between the frontend and backend.
4.  **Violation of ADR-016**: The silent failure to display images directly violated the "fail fast" and "no misleading content" principles established in ADR-016.

## Decision

**We will implement a centralized and automated data transformation layer within the frontend API client (`src/lib/api.ts`).**

This strategy establishes a clear contract:

1.  **Backend Convention**: The Python/FastAPI backend will **always** return JSON with `snake_case` keys. This is the standard convention and will be enforced.
2.  **Frontend Convention**: The TypeScript frontend will **always** use `camelCase` properties in its state and components. All TypeScript `interface` and `type` definitions will adhere to this.
3.  **Centralized Transformation**: A utility will be created and used within the API client to recursively transform all incoming `snake_case` responses into `camelCase` objects before they are returned to any component. Conversely, any data sent *to* the backend will be transformed from `camelCase` to `snake_case`.

### Example Transformation Logic:

```typescript
// A utility to transform object keys
function transformKeys(obj: any, transformer: (key: string) => string): any {
  if (Array.isArray(obj)) {
    return obj.map(v => transformKeys(v, transformer));
  } else if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      acc[transformer(key)] = transformKeys(obj[key], transformer);
      return acc;
    }, {} as any);
  }
  return obj;
}

// snake_case to camelCase
const toCamel = (s: string) => s.replace(/([-_][a-z])/ig, ($1) => $1.toUpperCase().replace('-', '').replace('_', ''));

// API client usage
const response = await apiClient.get('/api/v1/content/some-endpoint');
return transformKeys(response.data, toCamel);
```

## Consequences

### Positive:
-   ✅ **Bug Reduction**: Eliminates an entire class of data mapping bugs.
-   ✅ **Code Consistency**: Enforces a single, clear data convention on both the frontend and backend.
-   ✅ **Developer Efficiency**: Developers no longer need to perform manual transformations or guess the shape of API data.
-   ✅ **Maintainability**: Centralizes the transformation logic in one place, making it easy to manage and update.
-   ✅ **Adherence to ADRs**: Upholds the principles of reliability and graceful failure.

### Negative:
-   ➖ **Initial Implementation Overhead**: Requires creating and integrating the key transformation utility into the existing API client.
-   ➖ **Minor Performance Cost**: A small, generally negligible performance hit on the frontend to transform incoming data. This is an acceptable trade-off for the massive improvement in reliability.

## Implementation Plan

1.  **Create a utility file** (`src/lib/utils.ts` or similar) for the key transformation functions (`transformKeys`, `toCamel`, `toSnake`).
2.  **Integrate the transformation** into the `apiClient`'s response interceptors or a wrapper around `apiClient` calls in `src/lib/api.ts`.
3.  **Review and refactor** all existing API calls in `src/lib/api.ts` to use this new transformation layer.
4.  **Update all TypeScript interfaces** to use `camelCase` exclusively.
5.  **Remove any manual transformations** that currently exist in the components (`IdeationPage.tsx`, etc.).
6.  **Create a `LessonsLearned-Log.md` entry** for this issue.

This ADR establishes a robust and maintainable solution to a persistent problem, ensuring the frontend and backend can evolve independently without breaking the data contract. 