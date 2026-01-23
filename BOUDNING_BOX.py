PROMPT_1 = """
GEMINI_HIGHLIGHTING_PROMPT = """### Student Answer Step Highlighting - Include Incorrect Attempts

**Task**: Analyze the faculty solution image to identify step-wise marking structure, then locate and highlight ALL corresponding attempts in the student's answer - whether correct or incorrect.

**You will receive:**
1. **Faculty Image**: Reference solution showing step-wise marks (numbers in parentheses on the right side)
2. **Student Image**: Student's handwritten answer (may contain errors, partial answers, or incorrect approaches)

**Critical Understanding:**
- **The student's answer may be WRONG, but you must still map it to faculty steps**
- Look for what the student ATTEMPTED to answer, not whether it's correct
- Map based on INTENT and CONTEXT, not correctness
- Even completely wrong answers should be highlighted if they address that step

**Step Identification Process:**

1. **Analyze Faculty Image Structure:**
   - Identify marks in parentheses on the right margin
   - Each mark indicator defines one assessable step
   - Count total number of marking steps
   - Understand what concept/calculation each step addresses

2. **Understand What Each Faculty Step Is About:**
   - Identify the PURPOSE of each step (setup, calculation, explanation, conclusion, etc.)
   - Note the type of content in each step (formula, numerical work, text, diagram)
   - Recognize the conceptual goal of each marked section

3. **Locate Student's ATTEMPT at Each Step:**
   - **Match by INTENT and CONTEXT, not correctness**
   - Look for where student attempted to address the same concept
   - Recognize different approaches to the same problem
   - Identify similar content types even if values/conclusions differ
   
   - **Common scenarios to handle:**
     - Student uses wrong approach → Still map to the corresponding step
     - Student makes errors → Still map to the step they were attempting
     - Student writes incorrect values → Still map to that step
     - Student's method differs → Map based on what they're trying to achieve
     - Student skips a step → Mark that step's coordinates as null

4. **Flexible Content Matching:**
   - **Formula/Equation steps**: Look for ANY mathematical expression, even if incorrect
   - **Calculation steps**: Look for numerical work, even with wrong values
   - **Explanation steps**: Look for descriptive text, even if conceptually wrong
   - **Diagram steps**: Look for any drawn figure, even if poorly drawn
   - **Answer steps**: Look for final statements or conclusions, even if incorrect

5. **Intent-Based Mapping Principle:**
   - Focus on what the student is TRYING to do
   - Wrong formulas still map if they're attempting that concept
   - Wrong calculations still map if they're trying to compute that value
   - Wrong conclusions still map if they're addressing that question
   - Different notation or symbols still map if conceptually related

6. **Handle Extra Student Content:**
   
   **Case A - Content Related to Existing Step:**
   - If student writes content that doesn't appear in faculty solution (contextually)
   - BUT is related to one of the faculty steps
   - Determine which faculty step this extra content is

Output:
Return the student image with yellow boxes highlighting each attempted step, making it clear where the student addressed each marking point - whether correctly or incorrectly. Extra student content should be included within the most relevant step's bounding box.
"""
