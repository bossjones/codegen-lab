---
description: Guidelines for AI assistants to explain code modifications, especially deletions and changes
globs: *.*
alwaysApply: false
---

# AI Assistant Guidelines for Code Modifications

This rule provides comprehensive guidance for AI assistants when explaining code modifications, ensuring clear communication and understanding of changes.

<rule>
name: explain-code-modifications
description: Comprehensive guidelines for explaining code modifications
filters:
  - type: file_modification
    pattern: ".*"
actions:
  - type: suggest
    message: |
      When modifying or deleting code, always follow these guidelines:

      1. Reference and Document Changes:
         - Quote the specific code being modified/removed
         - Explain the reasoning behind each change
         - Describe how functionality is preserved or improved
         - Highlight potential impacts on other code

      2. Structure Your Explanations:
         ```
         <old_code>
         // Code being removed or modified
         </old_code>

         <explanation>
         Detailed reasoning for the changes
         </explanation>

         <new_code>
         // Replacement code (if applicable)
         </new_code>
         ```

      3. Complex Changes Process:
         - Provide step-by-step reasoning
         - Consider multiple approaches
         - Evaluate impacts and tradeoffs
         - Document your decision process

      4. Large Codebase Guidelines:
         - Show relevant context first
         - Use clear section headers
         - Reference specific code locations
         - Maintain proper scope

      5. Verification Steps:
         - Provide usage examples
         - Include test cases
         - Consider edge cases
         - Suggest additional testing

      6. Preserve Original Intent:
         - Acknowledge original purpose
         - Maintain behavior unless requested
         - Seek confirmation for major changes
         - Document any behavioral differences

examples:
  - input: |
      // Old implementation
      let counter = 0;
      function incrementCounter() {
        counter += 1;
        document.getElementById('counter').innerText = counter;
        localStorage.setItem('counter', counter);
      }
  - output: |
      <old_code>
      // Manual counter implementation
      let counter = 0;
      function incrementCounter() {
        counter += 1;
        document.getElementById('counter').innerText = counter;
        localStorage.setItem('counter', counter);
      }
      </old_code>

      <explanation>
      This implementation has several issues:
      1. Uses direct DOM manipulation which is error-prone
      2. Lacks proper error handling for localStorage
      3. Doesn't leverage React's state management
      </explanation>

      <new_code>
      // React-based implementation with proper error handling
      const [counter, setCounter] = useState(parseInt(localStorage.getItem('counter') || '0'));

      const incrementCounter = useCallback(() => {
        setCounter(prev => {
          const newValue = prev + 1;
          try {
            localStorage.setItem('counter', newValue.toString());
          } catch (e) {
            console.error('Failed to save to localStorage:', e);
          }
          return newValue;
        });
      }, []);
      </new_code>
</rule>

metadata:
  priority: high
  version: 1.0
  tags:
    - code-modification
    - documentation
    - best-practices
    - explanation

# AI Assistant Guidelines for Code Modifications

<rule>
name: explain-code-deletions
description: When deleting code, always provide clear explanations of what was removed and why
filters:
  - type: file_modification
    pattern: ".*"
actions:
  - type: suggest
    message: |
      When deleting or significantly modifying existing code, always:
      1. Reference the specific code being removed
      2. Explain the reasoning behind the deletion
      3. Describe how functionality is preserved or improved (if applicable)
      4. Highlight potential impacts on other parts of the codebase
</rule>

<rule>
name: use-xml-tags
description: Use XML tags to clearly structure explanations and code examples
filters:
  - type: content
    pattern: ".*"
actions:
  - type: suggest
    message: |
      Structure your explanations with XML tags to improve clarity:

      ```
      <old_code>
      // Code being removed or modified
      </old_code>

      <explanation>
      Detailed reasoning for the changes
      </explanation>

      <new_code>
      // Replacement code (if applicable)
      </new_code>
      ```
</rule>

<rule>
name: step-by-step-reasoning
description: Provide clear step-by-step reasoning for complex code changes
filters:
  - type: file_modification
    pattern: ".*"
actions:
  - type: suggest
    message: |
      For complex code modifications, provide your reasoning in a sequential format:

      ```
      <reasoning>
      1. First, I identified [specific issue/pattern]
      2. This approach is problematic because [reasons]
      3. A better solution is [alternative approach]
      4. This improves [specific benefits]
      </reasoning>
      ```
</rule>

<rule>
name: long-context-handling
description: Best practices for explaining changes in large codebases
filters:
  - type: file_size
    min_size: 10000
actions:
  - type: suggest
    message: |
      When modifying large files:

      1. Place the relevant code context at the top of your explanation
      2. Use clear section headers and structure with XML tags
      3. Quote specific sections being modified before explaining changes
      4. Reference function/class names and line numbers when possible
</rule>

<rule>
name: verify-and-test
description: Verify modifications with examples or test cases
filters:
  - type: file_modification
    pattern: ".*"
actions:
  - type: suggest
    message: |
      After explaining significant code changes:

      1. Provide example usage to demonstrate the modified code works as expected
      2. Include simple test cases that verify functionality
      3. Highlight any edge cases that should be considered
      4. Suggest additional tests if appropriate
</rule>

<rule>
name: extended-thinking-for-complex-changes
description: Use extended thinking for complex code analysis
filters:
  - type: complexity
    threshold: high
actions:
  - type: suggest
    message: |
      For complex code changes:

      1. First explore multiple approaches in <thinking> tags
      2. Consider backward compatibility implications
      3. Evaluate performance impacts
      4. Only after thorough analysis, propose the optimal solution with clear reasoning
</rule>

<rule>
name: preserve-intent
description: Always preserve the original intent and functionality unless explicitly instructed otherwise
filters:
  - type: file_modification
    pattern: ".*"
actions:
  - type: suggest
    message: |
      When modifying code:

      1. Explicitly acknowledge the original purpose of the code
      2. Confirm your changes maintain the same behavior unless specifically requested otherwise
      3. If substantially changing functionality, seek confirmation first
      4. Highlight any behavioral differences introduced by your changes
</rule>

## Implementation Examples

### Example 1: Simple Code Deletion

```
<old_code>
// Manually track and update counter
let counter = 0;
function incrementCounter() {
  counter += 1;
  document.getElementById('counter').innerText = counter;
  localStorage.setItem('counter', counter);
}
</old_code>

<explanation>
I'm removing this manual counter implementation because:
1. It uses direct DOM manipulation which is error-prone
2. It lacks proper error handling for localStorage
3. The React state system provides a more reliable alternative
</explanation>

<new_code>
// Use React's useState for reliable state management
const [counter, setCounter] = useState(parseInt(localStorage.getItem('counter') || '0'));

const incrementCounter = useCallback(() => {
  setCounter(prev => {
    const newValue = prev + 1;
    try {
      localStorage.setItem('counter', newValue.toString());
    } catch (e) {
      console.error('Failed to save to localStorage:', e);
    }
    return newValue;
  });
}, []);
</new_code>
```

### Example 2: Complex Refactoring with Extended Thinking

```
<thinking>
Looking at this data fetching code, I see several issues:
1. It uses nested callbacks leading to "callback hell"
2. Error handling is inconsistent
3. There's no loading state management
4. API responses aren't validated

I could refactor this to:
- Option A: Use async/await pattern
- Option B: Implement a Promise chain
- Option C: Use a data fetching library like SWR or React Query

For a modern React codebase, Option C provides the most benefits with reduced code complexity and built-in caching. However, if minimizing dependencies is important, Option A would be best.

The async/await approach would maintain the same functionality while improving readability and error handling.
</thinking>

<old_code>
function fetchUserData(userId) {
  fetch(`/api/users/${userId}`)
    .then(response => response.json())
    .then(userData => {
      renderUserProfile(userData);
      fetch(`/api/users/${userId}/posts`)
        .then(response => response.json())
        .then(posts => {
          renderUserPosts(posts);
        })
        .catch(error => {
          console.error('Post fetch failed', error);
        });
    })
    .catch(error => {
      console.error('User fetch failed', error);
    });
}
</old_code>

<explanation>
I'm refactoring this nested fetch implementation because:
1. The nested callback structure ("callback hell") makes the code difficult to read and maintain
2. Error handling is split across multiple catch blocks
3. There's no loading state management
4. The fetch calls are sequential when they could be parallel

The new implementation uses async/await for improved readability and Promise.all for parallel requests.
</explanation>

<new_code>
async function fetchUserData(userId) {
  try {
    setIsLoading(true);

    // Fetch user data and posts in parallel
    const [userResponse, postsResponse] = await Promise.all([
      fetch(`/api/users/${userId}`),
      fetch(`/api/users/${userId}/posts`)
    ]);

    if (!userResponse.ok) throw new Error(`User fetch failed: ${userResponse.status}`);
    if (!postsResponse.ok) throw new Error(`Posts fetch failed: ${postsResponse.status}`);

    const userData = await userResponse.json();
    const posts = await postsResponse.json();

    renderUserProfile(userData);
    renderUserPosts(posts);

    return { userData, posts };
  } catch (error) {
    console.error('Data fetching failed:', error);
    setError(error.message);
    return null;
  } finally {
    setIsLoading(false);
  }
}
</new_code>
