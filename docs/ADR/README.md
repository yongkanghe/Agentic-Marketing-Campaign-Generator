# Architecture Decision Records (ADR)

**Author: JP + 2025-06-15**

## Purpose

This folder contains Architecture Decision Records (ADRs) that document the significant architectural decisions made during the development of the Video Venture Launch platform. Each ADR captures the context, decision, and consequences of important technical choices.

## ADR Format

Each ADR follows this structure:
- **Title**: Short descriptive title
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The situation that led to the decision
- **Decision**: The architectural decision made
- **Consequences**: The positive and negative outcomes

## Current ADRs

1. [ADR-001: Technology Stack Selection](./ADR-001-technology-stack.md)
2. [ADR-002: Enhanced Campaign Creation Workflow](./ADR-002-enhanced-campaign-creation.md)
3. [ADR-003: Backend ADK Implementation Strategy](./ADR-003-backend-adk-implementation.md)
4. [ADR-003: VVL Design System Framework](./ADR-003-VVL-Design-System-Framework.md)
5. [ADR-004: Local Database Design for MVP](./ADR-004-local-database-design.md)

## Creating New ADRs

When making significant architectural decisions:
1. Copy the template from `ADR-template.md`
2. Number sequentially (ADR-XXX)
3. Fill in all sections thoroughly
4. Get team review before marking as "Accepted"
5. Update this README with the new ADR

## ADR Lifecycle

- **Proposed**: Initial draft, under discussion
- **Accepted**: Decision approved and implemented
- **Deprecated**: No longer recommended but still in use
- **Superseded**: Replaced by a newer ADR 