---
description: Anthropic Model Context Protocol (MCP) Specification Reference
globs: "**/*.py,**/*.md"
---

# Anthropic Model Context Protocol (MCP) Reference

## Overview

The Model Context Protocol (MCP) is a standardized communication protocol designed for interaction between LLM clients and servers. It enables clients to access resources, call tools, and exchange messages in a structured format.

## Core Concepts

### Protocol Structure

- JSON-RPC 2.0 based
- Bidirectional communication
- Request/response pattern with notifications
- Support for resource discovery and manipulation
- Support for prompt templates
- Support for tool invocation

### Communication Types

1. **Requests**: Messages that expect a response
2. **Notifications**: Messages that do not expect a response
3. **Results**: Responses to requests

## Protocol Flow

### Initialization

1. Client connects and sends `initialize` request with capabilities
2. Server responds with `InitializeResult` containing its capabilities
3. Client sends `notifications/initialized` to complete initialization

### Core Interactions

- Resource discovery and reading
- Prompt retrieval and usage
- Tool invocation
- LLM sampling via client

## Message Components

### Roles

- `user`: Represents the end user
- `assistant`: Represents the AI assistant

### Content Types

- `TextContent`: Text provided to or from an LLM
- `ImageContent`: Image provided to or from an LLM
- `EmbeddedResource`: Contents of a resource embedded in a prompt or result

## Resources

Resources represent data that the server can provide to the client.

### Resource Types

- `Resource`: A known resource the server can read
- `ResourceTemplate`: A template for creating resource URIs
- `TextResourceContents`: Text content of a resource
- `BlobResourceContents`: Binary content of a resource

### Resource Operations

- `resources/list`: Get available resources
- `resources/templates/list`: Get available resource templates
- `resources/read`: Read a specific resource
- `resources/subscribe`: Subscribe to resource updates
- `resources/unsubscribe`: Unsubscribe from resource updates

## Prompts

Prompts represent templates for generating messages to an LLM.

### Prompt Components

- `Prompt`: A prompt or prompt template
- `PromptArgument`: An argument for a prompt template
- `PromptMessage`: A message in a prompt

### Prompt Operations

- `prompts/list`: Get available prompts
- `prompts/get`: Get a specific prompt
- `completion/complete`: Get completion options for an argument

## Tools

Tools represent functions that the client can call on the server.

### Tool Components

- `Tool`: Definition of a callable tool
- `CallToolRequest`: Request to invoke a tool
- `CallToolResult`: Result of a tool invocation

### Tool Operations

- `tools/list`: Get available tools
- `tools/call`: Call a specific tool

## Sampling

Sampling allows the server to request LLM responses from the client.

### Sampling Components

- `CreateMessageRequest`: Request to sample an LLM
- `CreateMessageResult`: Result of sampling
- `SamplingMessage`: A message in a sampling request/result
- `ModelPreferences`: Preferences for model selection

## Root Access

Roots allow servers to access specific directories or files.

### Root Components

- `Root`: A root directory or file
- `ListRootsRequest`: Request for available roots
- `ListRootsResult`: Result containing available roots
- `RootsListChangedNotification`: Notification of roots changes

## Progress Tracking

- `ProgressToken`: Token for associating notifications with requests
- `ProgressNotification`: Notification of progress updates

## Logging

- `LoggingLevel`: Severity level for log messages (debug, info, warning, etc.)
- `LoggingMessageNotification`: Notification of a log message
- `SetLevelRequest`: Request to set logging level

## JSON Schema Reference

### Key Schema Definitions

```json
{
  "Role": {
    "enum": ["assistant", "user"],
    "type": "string"
  },

  "TextContent": {
    "properties": {
      "text": { "type": "string" },
      "type": { "const": "text" }
    },
    "required": ["text", "type"]
  },

  "ImageContent": {
    "properties": {
      "data": { "format": "byte", "type": "string" },
      "mimeType": { "type": "string" },
      "type": { "const": "image" }
    },
    "required": ["data", "mimeType", "type"]
  },

  "EmbeddedResource": {
    "properties": {
      "resource": { /* TextResourceContents or BlobResourceContents */ },
      "type": { "const": "resource" }
    },
    "required": ["resource", "type"]
  }
}
```

## Implementation Guidelines

### Client Implementation

1. Initialize connection with server
2. Discover available resources, prompts, and tools
3. Handle resource updates and notifications
4. Support LLM sampling requests
5. Manage progress tracking and cancellations

### Server Implementation

1. Handle initialization with capabilities
2. Provide access to resources
3. Offer prompts and prompt templates
4. Implement tools for client invocation
5. Request LLM sampling when needed

## Versioning and Compatibility

- Protocol version is negotiated during initialization
- Clients and servers should specify supported versions
- Servers should respond with their preferred version
- Clients must disconnect if they cannot support the server's version

## Security Considerations

- Access control for resources
- Validation of tool inputs
- Human-in-the-loop for LLM sampling
- Proper handling of binary data

## References

- [Anthropic documentation](https://docs.anthropic.com/)
- [MCP GitHub repository](https://github.com/anthropics/anthropic-model-context-protocol)
- [RFC 6570 - URI Template](https://datatracker.ietf.org/doc/html/rfc6570)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
