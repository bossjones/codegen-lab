# Cursor Auto Rules Agile Workflow

Welcome to the documentation for integrating `cursor-auto-rules-agile-workflow` with your projects. This guide will help you implement a structured, AI-assisted agile development workflow in both greenfield (new) and brownfield (existing) projects using Cursor.

## 📚 Documentation Structure

This documentation is organized into several sections for easy navigation:

- [Agile Workflow Guide](./agile-readme.md) - Comprehensive guide to the agile workflow system
- [Cursor Rules Guide](./cursor-rules-readme.md) - Details about cursor rules implementation
- [Templates Guide](./templates-readme.md) - Information about available templates
- [Workflows Guide](./workflows-readme.md) - Specific workflow implementations
- [Notes Guide](./xnotes-readme.md) - Flexible notepad-based implementation

## 🚀 Quick Start

### For Greenfield Projects

1. Clone the repository:
   ```bash
   gh repo clone bmadcode/cursor-auto-rules-agile-workflow
   ```

2. Initialize the workflow:
   ```bash
   # Copy the rules and templates to your project
   cp -r cursor-auto-rules-agile-workflow/.cursor/* your-project/.cursor/
   ```

3. Start with the Product Requirements Document (PRD):
   - Create `.ai/prd.md` using Cursor's AI assistance
   - Follow the structured workflow in [Agile Workflow Guide](./agile-readme.md)

### For Brownfield Projects

1. Clone and initialize as above

2. Additional setup:
   ```bash
   # Create initial project analysis
   mkdir -p .ai/analysis
   # Use Cursor's AI to analyze existing codebase
   ```

3. Integration steps:
   - Review existing architecture
   - Create migration plan
   - Follow brownfield-specific guidelines in documentation

## 🔧 Implementation Options

1. **Rule-Based Implementation (Recommended)**
   - Automatic standards enforcement
   - Consistent structure
   - Located in `.cursor/rules/workflows/workflow-agile-manual`

2. **Notepad-Based Implementation**
   - Flexible and lightweight
   - Ideal for focused sessions
   - Uses `xnotes/` templates

## 📋 Key Features

- Structured Agile workflow with AI assistance
- Seamless integration with Cursor's AI capabilities
- Comprehensive documentation and templates
- Support for both new and existing projects
- Test-Driven Development (TDD) integration
- Automated documentation maintenance

## 🎯 Best Practices

1. **Documentation**
   - Keep PRD and Architecture documents updated
   - Document significant decisions
   - Maintain clear implementation notes

2. **Development**
   - Follow Test-Driven Development
   - Regular status updates
   - Consistent commit messages

3. **AI Integration**
   - Leverage AI for planning and implementation
   - Use appropriate context levels
   - Regular progress tracking

## 📖 Detailed Documentation

For more detailed information about specific aspects of the workflow, please refer to the individual documentation files linked above.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](../contributing.md) for details on how to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.
