 """Carefully extract all text content from the PDF, maintaining the exact order and formatting as it appears.
Preserve all mathematical equations, formulas, and special characters exactly as they appear in the PDF.
Do not add any headers, descriptions, or labels to the output.

Output only the extracted text content in the following format for an example:

[
{
question_number: 1,
ocr_text: 'This is the PV curve <diagram_1>',
diagrams: [
  {
    id: 'diagram_1',
    coordinates: 'n/a',
    diagram_class: 'graph or diagram'
  }
],
pages: [2]
}
]

Important Rules:
- The output must be a list of such question-answer objects.
- Each object must contain:
  - question_number in increasing order which is the question number of the content,Question numbers may appear in various formats—such as compound forms like 11. (1), 11. (2), or simple forms like 7, 8, 9. Always preserve the original numbering exactly as it appears in the document..
  - ocr_text: complete question (including the question number present) and answer content, including <diagram_1> if any diagram exists.
  - diagrams: 
     - If diagram exists → write: id: 'diagram_1', coordinates: 'n/a', and appropriate diagram_class ('graph' or 'diagram').
     - If no diagram → set: id: 'n/a', coordinates: 'n/a', diagram_class: 'n/a'.
  - pages: The page number of the content ,Must always be shown as a list of integers in square brackets.

- Understand the context to group full question-answer blocks together.
- Maintain the output structure and avoid inserting extra commentary or descriptions.
- Any text that is struck through (strikethrough formatting) must be completely ignored and excluded from the output.
- Ignore any template, header, footer, or decorative elements such as 'Date', 'Page', and similar non-content areas that do not contribute to the main educational material
"""



"""
Carefully extract all text content from the PDF, maintaining the exact order and formatting as it appears.
Preserve all mathematical equations, formulas, and special characters exactly as they appear in the PDF.
Do not add any headers, descriptions, or labels to the output.

Output only the extracted text content in the following format for an example:

[
{
question_number: 1,
ocr_text: 'This is the PV curve <diagram_1>',
diagrams: [
  {
    id: 'diagram_1',
    coordinates: 'n/a',
    diagram_class: 'graph or diagram'
  }
],
pages: [2]
}
]

Important Rules:
- The output must be a list of such question-answer objects.
- Each object must contain:
  - question_number in increasing order which is the question number of the content,Question numbers may appear in various formats—such as compound forms like 11. (1), 11. (2), or simple forms like 7, 8, 9. Always preserve the original numbering exactly as it appears in the document..
  - ocr_text: complete question (including the question number present) and answer content, including <diagram_1> if any diagram exists.
  - diagrams: 
     - If diagram exists → write: id: 'diagram_1', coordinates: 'n/a', and appropriate diagram_class ('graph' or 'diagram').
     - If no diagram → set: id: 'n/a', coordinates: 'n/a', diagram_class: 'n/a'.
  - pages: The page number of the content ,Must always be shown as a list of integers in square brackets.

- Understand the context to group full question-answer blocks together.
- Maintain the output structure and avoid inserting extra commentary or descriptions.
- Any text that is struck through (strikethrough formatting) must be completely ignored and excluded from the output.
- Ignore any template, header or headings of the page, footer, or decorative elements such as 'Date', 'Page'.
"""


 """
Carefully extract all text content from the PDF (Ignore any template, header or headings of the page, footer, or decorative elements such as 'Date', 'Page'.), maintaining the exact order and formatting as it appears.
Preserve all mathematical equations, formulas, and special characters exactly as they appear in the PDF.
Do not add any headers, descriptions, or labels to the output.

Output only the extracted text content in the following format for an example:

[
{
question_number: 1,
ocr_text: 'This is the PV curve <diagram_1>',
diagrams: [
  {
    id: 'diagram_1',
    coordinates: 'n/a',
    diagram_class: 'graph or diagram'
  }
],
pages: [2]
}
]

Important Rules:
- The output must be a list of such question-answer objects.
- Each object must contain:
  - question_number in increasing order which is the question number of the content,Question numbers may appear in various formats—such as compound forms like 11. (1), 11. (2), or simple forms like 7, 8, 9. Always preserve the original numbering exactly as it appears in the document..
  - ocr_text: complete question (including the question number present) and answer content, including <diagram_1> if any diagram exists.
  - diagrams: 
     - If diagram exists → write: id: 'diagram_1', coordinates: 'n/a', and appropriate diagram_class ('graph' or 'diagram').
     - If no diagram → set: id: 'n/a', coordinates: 'n/a', diagram_class: 'n/a'.
  - pages: The page number of the content ,Must always be shown as a list of integers in square brackets.

- Understand the context to group full question-answer blocks together.
- Maintain the output structure and avoid inserting extra commentary or descriptions.
- Any text that is struck through (strikethrough formatting) must be completely ignored and excluded from the output.
"""






















"""
 Version 2.ms- prompt for marking scheme - 
You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Science-SQP)
A Marking Scheme PDF (e.g. Science-MS)
Each main question may have multiple sub-questions and corresponding answers. Your job is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure. If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.
[
{
        "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id": "36",
    "question_ocr": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V",
            "diagram_description": null,
            "marks_of_solution_36_A_i": 1
          }
        },
        {
          "question_id_36_A_ii": "ii. Value of the resistance R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_ii": "Using Ohm’s Law: R2 = 6V / 0.5A = 12Ω",
            "diagram_description": null,
            "marks_of_solution_36_A_ii": 1
          }
        },
        {
          "question_id_36_B_i": "iii. Value of resistance R1.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_B_i": "p.d. across R1 = Total p.d. − p.d. across R2 − p.d. across 2Ω = 12V − 6V − 4V = 2V, Current through R1 = 2A, R1 = 2V / 2A = 1Ω",
            "diagram_description": null,
            "marks_of_solution_36_A_iii": 3
          }
        }
      ]
    }
  } 
  {
    "question_id": "39",
    "question_ocr": "<image_1> Full main question text from SQP, including intro/instruction if any.",
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?",
          "question_image_description": "<image_1>",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.",
            "diagram_description": "<image_1>",
            "marks_of_solution_39_A": 1
          }
        },
        {
          "question_id_39_B": "B. What kind of mirror is used in this reflecting telescope?",
          "question_image_description": null,
          "solution": {
            "solution_text_39_B": "Concave mirror",
            "diagram_description": null,
            "marks_of_solution_39_B": 1
          }
        },
        {
          "question_id_39_C": "C. Explain with reason what kind of optical device (type of lens or mirror) that is used at the eyepiece.",
          "question_image_description": null,
          "solution": {
            "solution_text_39_C": "A converging lens is used at the eyepiece to collect rays from the plane mirror and help the viewer see a real, erect image of the star.",
            "diagram_description": null,
            "marks_of_solution_39_C": 2
          }
        },
        {
          "question_id_39_D": "D. What is the role of the plane mirror in the telescope?",
          "question_image_description": null,
          "solution": {
            "solution_text_39_D": "The plane mirror laterally inverts the image formed by the curved mirror and directs the rays toward the eyepiece.",
            "diagram_description": null,
            "marks_of_solution_39_D": 2
          }
        }
      ]
    }
  }
]
SPECIAL INSTRUCTIONS (Read Carefully)
-No Hallucinations: Do not add, complete, rephrase, or interpret any part of the question or answer. Extract word-for-word from the PDF. Don’t use your own knowledge. Just copy exactly what’s written.
-No Redundancy:
If the main question contains shared instructions or diagrams, do not repeat them in subparts.
Only include specific subquestion prompts in question_id_XX_A, XX_i, etc.
-Subquestion Logic:
Only create subquestions if they exist in the structure (like A, B, (i), etc.).
If there's only one question and answer, do not wrap it in a subquestions list.
-Diagrams:
Use <image_1>, <image_2>, etc., to reference diagrams.
Place them in question_image_description and diagram_description as applicable.
-Marking:
Use "solution_full_marks" for total marks at the main level.
-Use "marks_of_solution_XX" for each subpart.
OR-Based Questions:
If a question has Option A OR B, include both under subquestions.
-Visually Impaired Variant:
Treat these as separate questions using a suffix like "question_id": "39_v".
Clean Output:
-Strip out all irrelevant headers, footers, page numbers, and line breaks.
Output Rules
Return only the final JSON array
No markdown
No commentary
No extra formatting
Fully machine-readable and clean
"""




"""
V2-MS - Improvment in HANDELING OPTIONAL QUESTIONS

You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Science-SQP)
A Marking Scheme PDF (e.g. Science-MS)
Each main question may have multiple sub-questions and corresponding answers. Your job is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure. If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.
[
{
        "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id": "36",
    "question_ocr": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V",
            "diagram_description": null,
            "marks_of_solution_36_A_i": 1
          }
        },
        {
          "question_id_36_A_ii": "ii. Value of the resistance R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_ii": "Using Ohm’s Law: R2 = 6V / 0.5A = 12Ω",
            "diagram_description": null,
            "marks_of_solution_36_A_ii": 1
          }
        },
        {
          "question_id_36_B_i": "iii. Value of resistance R1.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_B_i": "p.d. across R1 = Total p.d. − p.d. across R2 − p.d. across 2Ω = 12V − 6V − 4V = 2V, Current through R1 = 2A, R1 = 2V / 2A = 1Ω",
            "diagram_description": null,
            "marks_of_solution_36_A_iii": 3
          }
        }
      ]
    }
  } 
  {
    "question_id": "39",
    "question_ocr": "<image_1> Full main question text from SQP, including intro/instruction if any.",
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?",
          "question_image_description": "<image_1>",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.",
            "diagram_description": "<image_1>",
            "marks_of_solution_39_A": 1
          }
        },
        {
          "question_id_39_B": "B. What kind of mirror is used in this reflecting telescope?",
          "question_image_description": null,
          "solution": {
            "solution_text_39_B": "Concave mirror",
            "diagram_description": null,
            "marks_of_solution_39_B": 1
          }
        },
        {
          "question_id_39_C": "C. Explain with reason what kind of optical device (type of lens or mirror) that is used at the eyepiece.",
          "question_image_description": null,
          "solution": {
            "solution_text_39_C": "A converging lens is used at the eyepiece to collect rays from the plane mirror and help the viewer see a real, erect image of the star.",
            "diagram_description": null,
            "marks_of_solution_39_C": 2
          }
        },
        {
          "question_id_39_D": "D. What is the role of the plane mirror in the telescope?",
          "question_image_description": null,
          "solution": {
            "solution_text_39_D": "The plane mirror laterally inverts the image formed by the curved mirror and directs the rays toward the eyepiece.",
            "diagram_description": null,
            "marks_of_solution_39_D": 2
          }
        }
      ]
    }
  }
]
SPECIAL INSTRUCTIONS (Read Carefully)
-No Hallucinations: Do not add, complete, rephrase, or interpret any part of the question or answer. Extract word-for-word from the PDF. Don’t use your own knowledge. Just copy exactly what’s written.
-No Redundancy:
If the main question contains shared instructions or diagrams, do not repeat them in subparts.
Only include specific subquestion prompts in question_id_XX_A, XX_i, etc.
-Subquestion Logic:
Only create subquestions if they exist in the structure (like A, B, (i), etc.).
If there's only one question and answer, do not wrap it in a subquestions list.
-Diagrams:
Use <image_1>, <image_2>, etc., to reference diagrams.
Place them in question_image_description and diagram_description as applicable.
-Marking:
Use "solution_full_marks" for total marks at the main level.
-Use "marks_of_solution_XX" for each subpart.
OR-Based Questions:
In case of a question has options to choose subquestions capture that into the question text 
-Visually Impaired Variant:
Treat these as separate questions using a suffix like "question_id": "39_v".
Clean Output:
-Strip out all irrelevant headers, footers, page numbers, and line breaks.
Output Rules
Return only the final JSON array
No markdown
No commentary
No extra formatting
Fully machine-readable and clean
Collapse
"""