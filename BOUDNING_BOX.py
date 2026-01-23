PROMPT_1 = """
GEMINI_HIGHLIGHTING_PROMPT = ### Student Answer Step Highlighting - Include Incorrect Attempts

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


PROMPT_2 = """
GEMINI_HIGHLIGHTING_PROMPT =### Student Answer Step Highlighting - Include Incorrect Attempts

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

6. **Handle Extra Student Content (Not in Faculty Solution):**
   - **If student writes content that doesn't appear in faculty solution (contextually)**
   - Determine which faculty step this extra content is RELATED to
   - Include this extra content within the bounding box of that related step
   - Expand the bounding box to encompass this additional student content
   - The extra content should be inside the box of the step it's most conceptually connected to

7. **Draw Yellow Highlight Boxes:**
   - Highlight the student's ATTEMPT for each step, regardless of correctness
   - One yellow box per step from faculty solution
   - Color: RGB(255, 255, 0) with 35% opacity
   - Include all related content even if scattered or messy
   - Include extra student content within the appropriate step's box
   - If student completely skipped a step, don't draw a box for it

**Mapping Priority Rules:**
1. **Primary**: What is the student trying to answer? (matches faculty step purpose)
2. **Secondary**: Where does similar content type appear? (equation, number, text, diagram)
3. **Tertiary**: Positional order in the solution (sequence of attempts)
4. **Extra Content**: Which step is this most conceptually related to?

**Handle These Cases:**

- **Wrong formulas/equations**: Map to formula step if student attempted any related expression
- **Calculation errors**: Map to calculation step if student showed any numerical work
- **Missing steps**: Don't highlight - return null coordinates for that step
- **Extra content**: Include within the box of the most related faculty step
- **Different approach**: Map based on logical equivalence of purpose
- **Partial attempts**: Highlight whatever student wrote for that step
- **Messy work**: Include cross-outs and corrections if they're the attempt
- **Scattered content**: Expand box to include all parts addressing that step
- **Additional explanations**: Include in the step box they're elaborating on

**Visual Marking Pattern:**
- Mark indicators on right side show step boundaries
- Content between consecutive marks = one complete step
- Number of steps = number of mark indicators
- Each step tests a specific concept/skill

**Highlighting Specifications:**
- Color: Yellow #FFFF00
- Opacity: 35% (keep student's work visible)
- Border: 2-3px outline for clarity
- Padding: 8-12 pixels around content
- Coverage: Include everything student wrote for that step PLUS any extra related content

**Output:**
Return the student image with yellow boxes highlighting each attempted step, making it clear where the student addressed each marking point - whether correctly or incorrectly. Extra student content should be included within the most relevant step's bounding box.

**Remember:**
- You are mapping ATTEMPTS, not validating correctness
- Wrong answers still get highlighted if they address that step
- Extra student content gets included in the related step's box
- The goal is to show WHERE the student tried to answer WHAT
- Correctness assessment happens separately - your job is spatial mapping only
"""
