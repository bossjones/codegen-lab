# Cursor Templates System Documentation

## Overview

The Cursor Templates system provides standardized document structures that work in tandem with the Agile workflow and rules systems. Templates ensure consistency across project documentation and enable AI assistants to generate properly formatted documents with all required sections.

## What Are Cursor Templates?

Cursor templates are Markdown files stored in the `.cursor/templates/` directory that define the structure and content requirements for various project documents. They serve as blueprints that:

1. Establish consistent document formats
2. Ensure all required sections are included
3. Provide examples of proper document structure
4. Guide AI assistants in document generation

## Core Templates

The repository includes three essential templates for the Agile workflow:

### 1. Product Requirements Document (PRD)

**File:** `.cursor/templates/template-prd.md`

The PRD template establishes the structure for defining project requirements, including:

- Project title and version
- Approval status tracking
- Introduction and goals
- Features and requirements
- Epic and story organization
- Technology stack
- Reference materials and diagrams
- Data models and API specifications
- Project structure
- Change log

This template ensures all critical project information is captured and organized consistently.

### 2. Architecture Document

**File:** `.cursor/templates/template-arch.md`

The architecture template provides a framework for documenting technical design decisions:

- System overview
- Component architecture
- Data flow diagrams
- API specifications
- Security considerations
- Scalability plans
- Technology choices
- Integration points
- Development patterns

This document serves as the technical blueprint for project implementation.

### 3. Story Template

**File:** `.cursor/templates/template-story.md`

The story template structures the implementation details for individual user stories:

- Story title and ID
- Status tracking (Draft, In Progress, Complete)
- Acceptance criteria
- Task breakdown with status tracking
- Implementation notes
- Testing requirements
- Completion checklist
- Chat log for context retention

This template ensures consistent tracking of implementation progress and requirements.

## How Templates Are Used

Templates are referenced by the workflow rules to guide document creation:

1. The workflow rule detects the need for a specific document
2. The rule directs the AI to use the appropriate template
3. The AI creates a new document following the template structure
4. The document is populated with project-specific content
5. The user reviews and approves the document
6. The document serves as a reference for subsequent work

## Template System Benefits

The templates system provides several key advantages:

1. **Consistency** - All documents follow standardized formats
2. **Completeness** - Templates ensure no critical sections are missed
3. **Efficiency** - AI assistants can generate well-structured documents quickly
4. **Knowledge Retention** - Templates capture institutional knowledge about document requirements
5. **Reduced Cognitive Load** - Users don't need to remember document structure requirements

## Integration with Rules

Templates work closely with the rules system:

- Workflow rules reference templates to guide document creation
- Templates include examples that help train AI behavior
- Both systems work together to maintain project consistency

## Working with Templates

### Accessing Templates

Templates are stored in the `.cursor/templates/` directory and can be:

- Referenced directly by the AI
- Modified by users to meet specific project needs
- Extended with additional templates as required

### Customizing Templates

While templates provide standardized structures, they can be customized:

1. Add project-specific sections
2. Adjust formatting to meet team preferences
3. Extend examples to better illustrate requirements
4. Modify language to match organizational terminology

### Creating New Templates

To create additional templates:

1. Create a new Markdown file in the `.cursor/templates/` directory
2. Follow the existing template pattern with clear section headings
3. Include examples where appropriate
4. Add placeholders with curly braces for variable content
5. Include any necessary explanatory comments

## Best Practices

1. **Maintain Template Integrity** - Keep core sections to ensure AI can properly follow them
2. **Use Clear Section Headings** - Makes documents easier to navigate
3. **Include Examples** - Helps both users and AI understand requirements
4. **Keep Templates Updated** - Evolve templates as project needs change
5. **Balance Detail and Flexibility** - Provide enough structure without being overly prescriptive
6. **Use Consistent Formatting** - Establish patterns that are easy to follow

## Conclusion

The Templates system is a key component of the Agile workflow, providing structure and consistency to project documentation. By using templates effectively, teams can ensure that all critical information is captured and organized in a way that supports efficient development and clear communication.
