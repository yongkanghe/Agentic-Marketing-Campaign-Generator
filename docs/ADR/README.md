# Architecture Decision Records (ADR)

**Author: JP + 2025-06-15**  
**Last Updated: 2025-06-25**

## Purpose

This folder contains Architecture Decision Records (ADRs) that document the significant architectural decisions made during the development of the AI Marketing Campaign Post Generator platform. Each ADR captures the context, decision, and consequences of important technical choices.

## ADR Format

Each ADR follows this structure:
- **Title**: Short descriptive title
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The situation that led to the decision
- **Decision**: The architectural decision made
- **Consequences**: The positive and negative outcomes

## Current ADRs Status Table

| ADR | Title | Status | Notes |
|-----|-------|--------|-------|
| [ADR-001](./ADR-001-technology-stack.md) | Technology Stack Selection | ✅ Accepted | Core tech stack |
| [ADR-002](./ADR-002-enhanced-campaign-creation.md) | Enhanced Campaign Creation Workflow | ✅ Accepted | Campaign UX |
| [ADR-003](./ADR-003-backend-adk-implementation.md) | Backend ADK Implementation Strategy | ✅ Accepted | ADK integration |
| [ADR-003](./ADR-003-VVL-Design-System-Framework.md) | VVL Design System Framework | ✅ Accepted | UI framework |
| [ADR-004](./ADR-004-environment-variable-standardization.md) | Environment Variable Standardization | ✅ Accepted | Config management |
| [ADR-004](./ADR-004-local-database-design.md) | Local Database Design for MVP | ✅ Accepted | Database schema |
| [ADR-005](./ADR-005-Social-Media-Post-Generation-Enhancement.md) | Social Media Post Generation Enhancement | ✅ Accepted | Content generation |
| [ADR-009](./ADR-009-real-ai-analysis-implementation.md) | Real AI Analysis Implementation | ✅ Accepted | AI analysis |
| [ADR-010](./ADR-010-API-timeout-configuration.md) | API Timeout Configuration | ✅ Accepted | API reliability |
| [ADR-011](./ADR-011-Near-Live-Testing-Strategy.md) | Near-Live Testing Strategy | ✅ Accepted | Testing approach |
| [ADR-012](./ADR-012-Campaign-Content-Caching-Architecture.md) | Campaign Content Caching Architecture | ✅ Accepted | Performance |
| [ADR-013](./ADR-013-Visual-Content-File-Storage.md) | Visual Content File Storage | ✅ Accepted | File management |
| [ADR-014](./ADR-014-video-content-generation-architecture.md) | Video Content Generation Architecture | ✅ Accepted | Video generation |
| [ADR-015](./ADR-015-real-video-file-storage-architecture.md) | Real Video File Storage Architecture | ✅ Accepted | Video storage |
| [ADR-016](./ADR-016-campaign-creative-guidance-validation.md) | Campaign Creative Guidance Validation | ✅ Accepted | Error handling |
| [ADR-017](./ADR-017-Frontend-Backend-API-Data-Transformation-Strategy.md) | Frontend-Backend API Data Transformation | ❌ **Superseded** | **Replaced by ADR-018** |
| [ADR-018](./ADR-018-Backend-CamelCase-API-Contract.md) | Backend CamelCase API Contract | 🟢 **Accepted** | **Current implementation** |

## Architectural Evolution

### Data Contract Strategy Evolution
- **ADR-017** → **ADR-018**: Moved from frontend transformation to backend camelCase
- **Reason**: Frontend complexity and runtime errors with null/undefined values
- **Result**: Simpler, more robust data contract with backend responsibility

## Creating New ADRs

When making significant architectural decisions:
1. Copy the template from `ADR-template.md`
2. Number sequentially (ADR-XXX)
3. Fill in all sections thoroughly
4. Get team review before marking as "Accepted"
5. Update this README with the new ADR
6. If superseding an existing ADR, mark the old one as "Superseded" with cross-reference

## ADR Lifecycle

- **Proposed**: Initial draft, under discussion
- **Accepted**: Decision approved and implemented
- **Deprecated**: No longer recommended but still in use
- **Superseded**: Replaced by a newer ADR (cross-referenced)

## Legend

- ✅ **Accepted**: Currently implemented and active
- 🟢 **Current**: Most recent decision in this area
- ❌ **Superseded**: Replaced by newer ADR
- ⚠️ **Deprecated**: Still in use but not recommended 