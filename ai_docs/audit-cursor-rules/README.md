# 🎨 Using the Workflow Rule Visualization Agent

Hey there! Let me explain how to use our special tool that helps us see how our cursor rules work together - just like a big colorful map! 🗺️

### What Does It Do?

Think of this tool like a detective that finds out which rules are being used in your code and how much space they take up. It helps us:
- See which rules are being used a lot (like your favorite toys!) 🎯
- Find rules that might be making our computer work too hard (like carrying too many toys at once) 🏋️
- Make special diagrams that show how everything connects (like connect-the-dots!) 🖼️

> From the agent definition: "This agent specializes in analyzing and visualizing when and how Cursor Rules get automatically invoked, tracking the total context they add to LLM prompts, and identifying overlapping or redundant rules."

### How to Use It

1. When you want to see how rules work together, just ask like this:
   ```
   @workflows/workflow-rule-visualization-agent-manual.mdc update the mermaid docs for prod

   ```

2. The agent will then use special commands to analyze your rules:
   ```
   make audit-cursor-rules-prod-desc  # for production environment
   ```
   or (if you say stage)
   ```
   make audit-cursor-rules-stage-desc  # for staging environment
   ```

3. It counts how many words (tokens) each rule has using:
   ```
   uv run python scripts/token_counter.py -f .cursor/rules/path/to/rule.mdc
   ```

4. Then the agent will:
   - Count how many words are in each rule (like counting blocks) 🧱
   - Make special Mermaid diagrams showing how rules connect (like a treasure map) 🗺️
   - Tell you which rules are used the most (like your favorite toys) ⭐
   - Suggest ways to make everything work better! 🧹

### What You'll Get

- Mermaid diagrams that show how rules work together 📊
- A list of which rules are biggest and smallest 📏
- Ideas on how to make everything work better 💡

> From the agent definition: "Generate Mermaid diagrams showing rule activation patterns" and "Provide specific recommendations for rules to convert to manual invocation, rules to consolidate or remove due to overlap."

### Where Results Are Saved

The agent creates folders to save all its work:
```
ai_docs/audit-cursor-rules/prod/   # for production environment
```
or
```
ai_docs/audit-cursor-rules/stage/  # for staging environment
```

### Example

Here's what happens when you use it:
1. It looks at all your rules
   - Runs a special command to analyze them
   - Counts how many words are in each rule using `token_counter.py`

2. It creates Mermaid diagrams showing how they connect
   - Shows which rules work together
   - Shows how many words each rule has

3. It tells you if any rules are too big
   - Finds rules using too many words
   - Suggests ways to make them smaller

4. It gives you ideas to make things better!
   - Suggests which rules should be manual instead of automatic
   - Helps you organize your rules better

> From the agent definition: "Identify rules that should be converted to manual invocation or removed" and "Categorize rules by token usage: Low impact (< 500 tokens), Medium impact (500-2000 tokens), High impact (> 2000 tokens)."

Remember: Just like organizing your toys makes playtime more fun, organizing our rules makes our code work better! 🌟

### Need Help?

If you ever get stuck or want to learn more about how the tools work, you can:
1. Look at the scripts in the `scripts` folder
2. Ask for help with a specific script (like "help me understand token_counter.py")
3. Try running the visualization agent with different commands

Have fun organizing your rules! 🎮
