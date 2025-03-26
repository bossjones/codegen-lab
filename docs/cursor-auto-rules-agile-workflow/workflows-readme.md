# Cursor Workflows System Documentation

## Overview

The Cursor Workflows system provides structured processes that guide AI assistants through complex development tasks. Workflows combine rules and templates to create repeatable, consistent development patterns that maintain project focus and context across multiple interactions.

## What Are Cursor Workflows?

Cursor workflows are rule-based processes that:

1. Establish a sequence of development activities
2. Enforce consistency across the development lifecycle
3. Maintain context and project memory
4. Guide AI assistants through complex tasks
5. Ensure adherence to project standards

## Workflow Implementation

Workflows are implemented as specialized rule files in the `.cursor/rules/workflows/` directory. The primary workflow in this repository is:

- **Agile Workflow** - `.cursor/rules/workflows/workflow-agile-manual.mdc`

This rule file defines the sequence, requirements, and constraints for the Agile development process.

## Workflow Components

A complete workflow consists of multiple interconnected elements:

1. **Workflow Rule** - The rule file that defines the process
2. **Templates** - Document structures referenced by the workflow
3. **Directory Structure** - Organized file locations for artifacts
4. **Status Tracking** - Mechanisms to track progress
5. **Context Retention** - Methods to maintain project memory

## The Agile Workflow

The Agile workflow implements a structured development process with distinct phases:

### 1. Initial Planning Phase

- PRD creation and approval
- Architecture design and approval
- Epic planning
- Story definition

### 2. Development Phase

- Story implementation
- Task execution
- Testing and validation
- Story completion

### 3. Iteration

- Progression to next story
- Epic completion
- Project release

## Workflow Process

The Agile workflow follows a specific sequence:

1. **Project Initialization**
   - AI checks for .ai/prd.md existence
   - If not present, assists user in creating one
   - Ensures PRD is comprehensive and approved

2. **Architecture Definition**
   - Once PRD is approved, AI assists in architecture creation
   - Architecture document (.ai/arch.md) is developed using the template
   - User reviews and approves architecture

3. **Story Development**
   - AI generates first/next story from the PRD
   - Story is marked as Draft until user approves
   - Once approved and marked In Progress, implementation begins
   - Tasks are completed and tracked in the story file
   - Testing is performed to verify completion
   - Story is marked Complete when all tasks are done

4. **Project Progression**
   - After completing a story, AI generates the next story
   - Process repeats until all stories in the current Epic are complete
   - When an Epic is complete, process moves to the next Epic
   - Project is complete when all Epics are implemented

## Project Memory Structure

The workflow maintains project context through a structured file organization:

```
.ai/
├── prd.md                 # Product Requirements Document
├── arch.md                # Architecture Decision Record
├── epic-1/               # Current Epic directory
│   ├── story-1.story.md  # Story files for Epic 1
│   ├── story-2.story.md
│   └── story-3.story.md
├── epic-2/               # Future Epic directory
│   └── ...
└── epic-3/               # Future Epic directory
    └── ...
```

This structure serves as the AI's "memory" of the project, allowing it to maintain context across multiple sessions.

## Critical Workflow Rules

The Agile workflow enforces several critical rules:

1. Never creates first story without PRD and Architecture approval
2. Only one Epic can be in-progress at a time
3. Only one Story can be in-progress at a time
4. Stories must be implemented in PRD-specified order
5. Never implement without story approval from user (marked as in progress)

## How to Use the Workflow

To use the Agile workflow:

1. **Start a new Agent chat** with your preferred AI model
2. **Reference the workflow** with `@workflow-agile-manual`
3. **Describe your project** needs and requirements
4. **Collaborate with the AI** to create the PRD
5. **Approve the PRD** by changing its status to "Approved"
6. **Continue the process** following the workflow sequence

Example prompt:
```
Let's follow the @workflow-agile-manual to create a PRD for a new project that will [project description]. Let's focus on just the MVP features first, but also plan some epics for future enhancements.
```

## Benefits of the Workflow System

Using structured workflows provides numerous advantages:

1. **Consistency** - Development follows a predictable pattern
2. **Completeness** - No critical steps are missed
3. **Context Retention** - Project memory is maintained across sessions
4. **Quality Control** - Testing and validation are built into the process
5. **Progress Tracking** - Status is clearly visible at all times
6. **Knowledge Sharing** - Process is documented and shareable

## Workflow Types

The system supports different workflow configurations:

1. **Rule-Based Implementation** (Recommended)
   - Uses `.cursor/rules/workflows/workflow-agile-manual.mdc`
   - Automatically applies standards to matching files
   - Provides consistent structure enforcement

2. **Notepad-Based Implementation** (Alternative)
   - Uses templates in `xnotes/` directory
   - Lighter weight and more adaptable
   - Ideal for simpler projects

## Customizing Workflows

Workflows can be customized to meet specific project needs:

1. Modify the workflow rule to adjust the process
2. Create variations of workflows for different project types
3. Adjust templates referenced by the workflow
4. Extend the project structure as needed

## Best Practices

1. **Start Fresh Contexts** - Begin a new chat session for each major workflow phase
2. **Regular Updates** - Keep story status and notes current
3. **Commit Often** - Save progress regularly with version control
4. **Clear Approvals** - Explicitly mark documents as approved
5. **Maintain Documentation** - Keep PRD and Architecture updated as the project evolves
6. **TDD Approach** - Follow test-driven development practices
7. **Context Management** - Be mindful of AI context limitations

## Conclusion

The Workflows system provides a powerful framework for structured, consistent development with AI assistance. By following the defined processes, teams can maintain focus, preserve context, and deliver high-quality results efficiently.
