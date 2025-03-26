---
description: Use this rule when generating starter prompts for PRD creation that incorporate AI report summaries
globs:
alwaysApply: false
---

# PRD Prompt Generator with AI Report Integration

## Context
- Used when needing to generate structured prompts for PRD creation
- Requires an ai_report.md file in the workspace for context
- Helps maintain consistency in PRD requests while incorporating existing project insights

## Critical Rules

- Always read and analyze ai_report.md first for context
- Generate 3 distinct prompt variations with increasing complexity
- Include specific sections for:
  - MVP features
  - Future enhancements (epics)
  - Technical constraints
  - Integration points
- Reference workflow-agile-manual in each prompt
- Structure prompts to encourage iterative development
- Include placeholders for project-specific details marked with {brackets}
- Maintain focus on business value and user needs 📊
- Ensure prompts encourage clear success metrics 🎯

## Examples

<example>
"Let's follow the @workflow-agile-manual to create a PRD for {project_name}. The MVP will focus on {core_feature} based on our AI report insights. For future epics, we'll consider {enhancement_1} and {enhancement_2} as highlighted in our analysis. Key technical requirements include {requirement_1} from our existing architecture."

"Following workflows/workflow-agile-manual.mdc, let's develop a PRD that builds upon our AI report findings. The core MVP will deliver {specific_feature}, integrating with {existing_system}. Future enhancements will include {epic_1} and {epic_2}, aligning with our technical roadmap."

"Based on our AI report's recommendations, let's use @workflow-agile-manual to craft a PRD for {project_scope}. We'll prioritize {mvp_feature} for immediate delivery, while planning future epics for {enhancement_area}. This aligns with our current {technical_framework} while preparing for {future_integration}."
</example>

<example type="invalid">
"Let's create a PRD without considering the AI report insights"

"Create a full product spec with all features at once"

"Let's build everything in the first release without MVP planning"
</example>
