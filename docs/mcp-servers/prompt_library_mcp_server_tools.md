#   Prompt Library MCP Server Tools

    This document describes the MCP tools available in the Prompt Library server for managing cursor rules and repository analysis.

    ##   Core Tools

    ###   Repository Analysis

    -   `instruct_repo_analysis`: Runs a repository analysis to gather information for cursor rule creation. This tool analyzes the repository structure and content to provide insights for generating appropriate cursor rules.

    -   `instruct_custom_repo_rules_generation`: Executes a cursor rules generation process based on repository analysis. Takes a repository summary as input and generates custom cursor rules based on the identified technologies and patterns.

    ###   Static Rule Management

    -   `get_static_cursor_rule`: Retrieves a specific cursor rule file by name to be written to the caller's `.cursor/rules` directory. Useful for getting individual predefined cursor rules.

    -   `get_static_cursor_rules`: Retrieves multiple cursor rule files to be written to the caller's `.cursor/rules` directory. Allows batch retrieval of predefined cursor rules.

        ```mermaid
        graph TD
        A[get_static_cursor_rules] --> B[get_static_cursor_rule]
        ```

    ###   Rule Creation and Management

    -   `save_cursor_rule`: Saves a cursor rule to the cursor rules directory in the project. Takes a rule name and content in MDC format as input.

    -   `recommend_cursor_rules`: Analyzes a repository summary and recommends cursor rules to generate based on identified technologies and patterns.

    ###   Workspace Preparation

    -   `prep_workspace`: Prepares the workspace for cursor rules by returning natural language instructions. Sets up the necessary directory structure and configuration.

    ###   File Management

    -   `create_cursor_rule_files`: Creates empty cursor rule files and provides instructions for sequential content creation. Useful for setting up new rule templates.

    ###   Makefile Integration

    -   `ensure_makefile_task`: Ensures the Makefile has the update-cursor-rules task. Verifies and adds necessary build automation.

    -   `process_makefile_result`: Processes the results of checking the Makefile and updates it if needed. Handles Makefile modifications.

    -   `run_update_cursor_rules`: Runs the update-cursor-rules Makefile task to deploy cursor rules. Executes the build automation.

    -   `process_update_cursor_rules_result`: Processes the results of checking the Makefile and runs the update-cursor-rules task if possible.

    -   `finalize_update_cursor_rules`: Processes the results of running the update-cursor-rules task. Handles completion and cleanup.

    ###   Docker Integration

    -   `update_dockerignore`: Updates the .dockerignore file to exclude the cursor rules drafts directory.

    -   `process_dockerignore_result`: Processes the results of checking the .dockerignore file and updates it if needed.

    ###   Workflow Management

    -   `cursor_rules_workflow`: Executes the complete cursor rules workflow. Orchestrates the entire process of rule creation and deployment.

        ```mermaid
        graph TD
        A[cursor_rules_workflow] --> B[prep_workspace]
        A --> C[create_cursor_rule_files]
        A --> D[ensure_makefile_task]
        A --> E[update_dockerignore]
        ```

    -   `process_cursor_rules_workflow_result`: Processes the results of executing the cursor rules workflow.

    ###   Advanced Workflow

    -   `plan_and_execute_prompt_library_workflow`: Executes a structured workflow for generating custom cursor rules based on repository analysis. This is a comprehensive tool that manages the entire process from analysis to rule generation.

        ```mermaid
        graph TD
        A[plan_and_execute_prompt_library_workflow] --> B[execute_phase_1]
        A --> C[execute_phase_2]
        A --> D[execute_phase_3]
        A --> E[execute_phase_4]
        A --> F[execute_phase_5]
        ```

    ##   Workflow Phases

    The prompt library implements a 5-phase workflow for cursor rule generation:

    1.  `execute_phase_1`: Initial repository analysis and setup

        ```mermaid
        graph TD
        A[execute_phase_1] --> B[prep_workspace]
        A --> C[repo_analysis_prompt]
        ```

    2.  `execute_phase_2`: Rule template creation and configuration

        ```mermaid
        graph TD
        A[execute_phase_2] --> B[recommend_cursor_rules]
        ```

    3.  `execute_phase_3`: Rule content generation and validation

        ```mermaid
        graph TD
        A[execute_phase_3] --> B[ensure_makefile_task]
        A --> C[update_dockerignore]
        A --> D[create_cursor_rule_files]
        ```

    4.  `execute_phase_4`: Rule deployment and integration

        ```mermaid
        graph TD
        A[execute_phase_4] --> B[save_cursor_rule]
        ```

    5.  `execute_phase_5`: Final verification and cleanup

        ```mermaid
        graph TD
        A[execute_phase_5] --> B[run_update_cursor_rules]
        ```

    Each phase is executed sequentially as part of the complete workflow, ensuring a systematic approach to cursor rule generation and management.
