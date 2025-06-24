# Low-Level Design (LLD): Solution Architecture & Data Flow

**Date**: 2025-06-25
**Status**: Active
**Author**: JP

## 1. Overview

This document provides a low-level design of the AI Marketing Campaign Post Generator, focusing on the data architecture, object structures, and data flow. The goal is to establish a clear and unambiguous data contract between the frontend, backend API, and the ADK-based agent system. This document is the canonical reference for all data objects and their properties.

### 1.1. System Components

-   **Frontend**: A React/TypeScript single-page application (SPA) responsible for user interaction, campaign management, and rendering generated content. It uses `camelCase` for all its internal state and object properties.
-   **Backend API**: A Python/FastAPI application that serves as the gateway between the frontend and the agentic system. Per **[ADR-018](./ADR-018-Backend-CamelCase-API-Contract.md)**, it automatically serializes all JSON responses to `camelCase` to match the frontend's convention.
-   **Agentic System (ADK)**: A multi-agent system built with the Google Agent Development Kit (ADK). It includes a `MarketingOrchestrator` that coordinates specialized agents for analysis, text generation, and visual content generation.

---

## 2. Data Flow Architecture

The generation of content follows a two-phase process: first text generation, then visual generation. This ensures a fast user response for text, while the more time-consuming visual generation happens subsequently.

### 2.1. Sequence Diagram

This diagram illustrates the simplified end-to-end data flow. The backend handles the data format convention, creating a seamless contract.

```mermaid
sequenceDiagram
    participant User
    participant Frontend (UI)
    participant Frontend (api.ts)
    participant Backend (API)
    participant Backend (Agents)

    User->>Frontend (UI): Clicks "Regenerate Text Content"
    Frontend (UI)->>Frontend (api.ts): generateBulkContent({postType: 'text_image', ...})
    
    Note over Frontend (api.ts): Request object uses camelCase.
    Frontend (api.ts)->>Backend (API): POST /api/v1/content/generate-bulk (camelCase payload)
    
    Backend (API)->>Backend (API): Pydantic automatically maps camelCase to snake_case models.
    Backend (API)->>Backend (Agents): Invoke text generation agent with snake_case context.
    Backend (Agents)-->>Backend (API): Return posts with snake_case (e.g., image_url: null).
    
    Note over Backend (API): Pydantic automatically serializes response to camelCase.
    Backend (API)-->>Frontend (api.ts): Respond with JSON (camelCase).
    
    Frontend (api.ts)-->>Frontend (UI): Return Promise with camelCase data.
    Frontend (UI)->>Frontend (UI): Update state with text-only posts (imageUrl is null).
    
    Note right of Frontend (UI): UI shows text, triggers visual generation.

    Frontend (UI)->>Frontend (api.ts): generateVisualContent({socialPosts: [...], ...})
    
    Frontend (api.ts)->>Backend (API): POST /api/v1/content/generate-visuals (camelCase payload)

    Backend (API)->>Backend (API): Pydantic maps request to snake_case.
    Backend (API)->>Backend (Agents): Invoke visual content agent with context.
    Backend (Agents)-->>Backend (API): Return posts with populated snake_case image_url.

    Note over Backend (API): Pydantic serializes response to camelCase.
    Backend (API)-->>Frontend (api.ts): Respond with JSON (camelCase).
    Frontend (api.ts)-->>Frontend (UI): Return Promise with camelCase data (imageUrl is now populated).

    Frontend (UI)->>User: Update state, render post with final image.
```

---

## 3. Data Transformation Strategy

As defined in **[ADR-018](./ADR-018-Backend-CamelCase-API-Contract.md)**, there is **no data transformation on the frontend**. The backend is solely responsible for providing a `camelCase` JSON API.

-   **API Contract**: The API serves `camelCase`. The frontend consumes `camelCase`.
-   **Simplicity**: This removes a layer of complexity and a potential source of errors from the frontend, leading to a more robust and maintainable system.

---

## 4. API Data Object Reference

This section details the structure of the primary data objects as consumed by the frontend.

### 4.1. `SocialMediaPost` Object

This is the core object representing a single piece of generated content.

| Property (`camelCase`) | Type     | Description                                                                 |
| ---------------------- | -------- | --------------------------------------------------------------------------- |
| `id`                   | `string` | Unique identifier for the post (UUID).                                      |
| `type`                 | `string` | The type of post, e.g., 'text_image', 'text_video', 'text_url'.             |
| `content`              | `string` | The main text body of the social media post.                                |
| `hashtags`             | `string[]` | An array of suggested hashtags.                                             |
| `imageUrl`             | `string \| null` | URL of the generated image. Is `null` after text generation.                |
| `videoUrl`             | `string \| null` | URL of the generated video. Is `null` after text generation.                |
| `productUrl`           | `string \| null` | The URL to the business's product or service page.                          |
| `engagementScore`      | `number` | An AI-predicted score for the post's potential engagement.                  |
| `platformOptimized`    | `object` | An object containing platform-specific guidance or notes.                   |
| `selected`             | `boolean`| A flag indicating if the user has selected the post for scheduling.         |
| `imagePrompt`          | `string \| null` | The final, enhanced prompt sent to the Imagen model.                        |
| `videoPrompt`          | `string \| null` | The final, enhanced prompt sent to the Veo model.                           |
| `error`                | `string \| null` | An error message if content generation failed for this specific item.       |


### 4.2. `BusinessContext` Object

This object carries the comprehensive campaign context used by all agents.

| Property (`camelCase`)  | Type     | Description                                                              |
| ------------------------- | -------- | ------------------------------------------------------------------------ |
| `companyName`             | `string` | Name of the business.                                                    |
| `objective`               | `string` | The primary goal of the marketing campaign (e.g., 'increase awareness'). |
| `campaignType`            | `string` | Type of campaign (e.g., 'brand', 'product').                             |
| `targetAudience`          | `string` | Description of the target audience.                                      |
| `businessDescription`     | `string` | A detailed description of the business.                                  |
| `businessWebsite`         | `string` | The main URL for the business.                                           |
| `productServiceUrl`       | `string` | A specific URL for a product or service.                                 |
| `campaignMediaTuning`     | `string` | User-provided fine-tuning instructions for visuals.                      |
| `campaignGuidance`        | `object` | AI-generated guidance object (contains themes, visual style, etc.).      |
| `productContext`          | `object` | AI-generated context for a specific product.                             |

### 4.3. `/generate-visuals` API Endpoint

-   **Request Payload:**
    ```typescript
    {
      socialPosts: SocialMediaPost[],
      businessContext: BusinessContext,
      campaignObjective: string,
      campaignId: string
    }
    ```
-   **Response Payload:**
    ```typescript
    {
      postsWithVisuals: SocialMediaPost[], // Now with imageUrl/videoUrl populated
      generationMetadata: object
    }
    ```

This LLD provides a solid foundation for understanding the data flow and object structures within the application, ensuring consistency and reducing bugs. 