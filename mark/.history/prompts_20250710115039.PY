''' VERSION 1 :
You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Science-SQP)
A Marking Scheme PDF (e.g. Science-MS)
Each main question may have multiple sub-questions and corresponding answers. Your task is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure. If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.

Follow the example below
[
         "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id_36": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1> explanation of the image_1",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V<Image_2>",
            "diagram_description": <Image_2> explanation of image_2,
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
    "question_id_39":"follow the questions in subquestions as mentioned"
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?<image_1>",
          "question_image_description": "<image_1> explanation of image_1",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.<image_2>",
            "diagram_description": "<image_2> explanation of image_2",
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
Fully machine-readable and clean text
'''
'''
=============================================================================================================================================================================================================================
VERSION 2 :
You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Maths-SQP)
A Marking Scheme PDF (e.g. Maths-MS)
Each main question may have multiple sub-questions and corresponding answers. Your task is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure. If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.

Follow the example below:
[
         "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id_36": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1> explanation of the image_1",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V<Image_2>",
            "diagram_description": <Image_2> explanation of image_2,
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
    "question_id_39":"follow the questions in subquestions as mentioned"
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?<image_1>",
          "question_image_description": "<image_1> explanation of image_1",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.<image_2>",
            "diagram_description": "<image_2> explanation of image_2",
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
Fully machine-readable and clean text


=============================================================================================================================================================================================================================
VERSION 3 :
You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Science-SQP)
A Marking Scheme PDF (e.g. Science-MS)
Each main question may have multiple sub-questions and corresponding answers. Your task is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure. If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.Include the question ID in the format: "question_id_38". Do not create a separate key for the question ID.Make sure the image id is present in question id .

Follow the example below Strictly:
[
         "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id_36": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1> explanation of the image_1",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V<Image_2>",
            "diagram_description": <Image_2> explanation of image_2,
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
    "question_id_39":"follow the questions in subquestions as mentioned"
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?<image_1>",
          "question_image_description": "<image_1> explanation of image_1",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.<image_2>",
            "diagram_description": "<image_2> explanation of image_2",
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
SPECIAL INSTRUCTIONS (Read Carefully and follow them accordingly )
-Mention the question id in this format "question_id_38" do not make a separate key for the question id 
-Make sure the <image_id> if present is mentioned in the key "question_id_38" and in the question_image_description.
-No Hallucinations: Do not add, complete, rephrase, or interpret any part of the question or answer. Extract word-for-word from the PDF. Don’t use your own knowledge. Just copy exactly what’s written.
-No Redundancy:
If the main question contains shared instructions or diagrams which is a part of a sub-question, do not repeat them in sub-question.
Only include specific subquestion prompts in question_id_XX_A, XX_i, etc.
-Subquestion Logic:
Only create subquestions if they exist in the structure (like A, B, (i), etc.).
If there's only one question and answer, do not wrap it in a subquestions list.
-Diagrams:
Use <image_1>, <image_2>, etc., to reference diagrams.
Place them in question_id_description and diagram_description as applicable.
-Marking:
Use "solution_full_marks" for total marks at the main level.
-Use "marks_of_solution_XX" for each subpart.
OR-Based Questions:
If a question has Option A OR B, include both under subquestions.
Clean Output:
-Strip out all irrelevant headers, footers, page numbers, and line breaks.
Output Rules
Return only the final JSON array
No markdown
No commentary
No extra formatting
Fully machine-readable and clean text



=============================================================================================================================================================================================================================
Version - 4 - or solution and marks
this is for or solutions where marks are not explicitly identified 
You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Science-SQP)
A Marking Scheme PDF (e.g. Science-MS)
Each main question may have multiple sub-questions and corresponding answers. Your task is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure and the content in the sub-questions must not be present in the main question . If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.Include the question ID in the format: "question_id_38". Do not create a separate key for the question ID.Make sure the image id is present in question id .

Follow the example below Strictly:
[
         "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id_36": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1> explanation of the image_1",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V<Image_2>",
            "diagram_description": <Image_2> explanation of image_2,
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
    "question_id_39":"Image of the star Explanatio"
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?<image_1>",
          "question_image_description": "<image_1> explanation of image_1",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.<image_2>",
            "diagram_description": "<image_2> explanation of image_2",
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
SPECIAL INSTRUCTIONS (Read Carefully and follow them accordingly )
-Please provide the marks for each line of the solution in a structured manner. For each solution, follow this format:
For each line of the solution, indicate the corresponding marks, breaking down the steps clearly and assigning appropriate marks.
If the question includes an "OR" between multiple parts, assign marks based on the individual sections, with each "OR" option receiving the same marks as the part it is related to, understand the context of the questions wherever "or" is placed .
For example:
{
  "question_id_25_B": "B. The above figure shows two resistors X and Y connected in series to a battery. The power dissipated for this combination is P1. When these resistors are connected in parallel to the same battery then the power dissipated is given by P2. Find out the ratio P1/P2.\n<image_1>",
  "question_image_description": "A circuit diagram showing two resistors, X (resistance R) and Y (resistance 2R), connected in series to a battery.",
  "solution": {
    "solution_text_25_B_1": "For series total resistance is R+2R = 3R",
    "marks_of_solution_1": 0.5,
    "solution_text_25_B_2": "P₁ = V²/3R",
    "marks_of_solution_2": 0.5,
    "solution_text_25_B_3": "For parallel total Resistance is 2R/3",
    "marks_of_solution_3": 0.5,
    "solution_text_25_B_4": "P₂ = V²/(2R/3) = 3V²/2R. P₁/P₂ = 2/9.",
    "marks_of_solution_4": 0.5
  }
}
-Mention the question id in this format "question_id_38" do not make a separate key for the question id 
-Make sure the <image_id> if present is mentioned in the key "question_id_38" and in the question_image_description.
-No Hallucinations: Do not add, complete, rephrase, or interpret any part of the question or answer. Extract word-for-word from the PDF. Don’t use your own knowledge. Just copy exactly what’s written.
-No Redundancy:
If the main question contains shared instructions or diagrams which is a part of a sub-question, do not repeat them in sub-question.
Only include specific subquestion prompts in question_id_XX_A, XX_i, etc.
-Subquestion Logic:
Only create subquestions if they exist in the structure (like A, B, (i), etc.).
If there's only one question and answer, do not wrap it in a subquestions list.
-Diagrams:
Use <image_1>, <image_2>, etc., to reference diagrams.
Place them in question_id_description and diagram_description as applicable.
-Marking:
Use "solution_full_marks" for total marks at the main level.
-Use "marks_of_solution_XX" for each subpart.
OR-Based Questions:
If a question has Option A OR B, include both under subquestions.
Clean Output:
-Strip out all irrelevant headers, footers, page numbers, and line breaks.
Output Rules
Return only the final JSON array
No markdown
No commentary
No extra formatting
Fully machine-readable and clean text

=========================================================================================================
Version - 5 SOLUTION MARKS AND OR Questions
You are an AI assistant tasked with extracting structured educational questions and solutions from PDFs.
You are given:
A Question Paper PDF (e.g. Science-SQP)
A Marking Scheme PDF (e.g. Science-MS)
Each main question may have multiple sub-questions and corresponding answers. Your task is to extract both the question and its marking scheme into one JSON file, in the exact structure below. Only create subquestion blocks (like question_id_22_A, question_id_22_i,question_id_22_) if they actually exist in the question structure and the content in the sub-questions must not be present in the main question . If the question and its solution  is standalone without labeled subparts, write it directly under question_id without duplicating it inside subquestions.Include the question ID in the format: "question_id_38". Do not create a separate key for the question ID.Make sure the image id is present in question id .

Follow the example below Strictly:
[
         "question_id_35": "Identify 'p', 'q' and 'r' in the following balanced reaction\nHeat\np Pb (NO3)2(s) ------> q PbO(s) + r NO2(g) + O2(g)\nΑ. 2,2,4\nB. 2,4,2\nC. 2,4,4\nD. 4,2,2",
            "question_image_description": null,
            "solution": {
              "solution_text_1": "Α. 2,2,4",
              "diagram_description": null,
              "marks_of_solution_1": 1
            }
  {
    "question_id_36": "<image_1> The above circuit is a part of an electrical device. Use the information given in the question to calculate the following.",
    "question_image_description": "<image_1> explanation of the image_1",
    "solution": {
      "solution_full_marks": "(5 marks)",
      "subquestions": [
        {
          "question_id_36_A_i": "i. Potential Difference across R2.",
          "question_image_description": null,
          "solution": {
            "solution_text_36_A_i": "p.d. across 4Ω resistor = p.d. across R2 = 1.5A × 4Ω = 6V<Image_2>",
            "diagram_description": <Image_2> explanation of image_2,
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
    "question_id_39":"Image of the star Explanatio"
    "question_image_description": "<image_1>",
    "solution": {
      "solution_full_marks": "(4 marks)",
      "subquestions": [
        {
          "question_id_39_A": "A. What kind of image of the star is seen by the observer at the eyepiece?<image_1>",
          "question_image_description": "<image_1> explanation of image_1",
          "solution": {
            "solution_text_39_A": "Real Image — formed due to the lens at the eyepiece.<image_2>",
            "diagram_description": "<image_2> explanation of image_2",
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
SPECIAL INSTRUCTIONS (Read Carefully and follow them accordingly )
Breakdown of Solution Marks:
-For each line of the solution, clearly indicate the corresponding marks, step by step as mentioned in the pdf. This should be done with clarity so that the solution steps align with the given marks for each part.
-Handling "OR" Between Questions:
If the question contains an "OR" between multiple parts, treat the "OR" as separating two possible solutions for a single question.
-The solution associated with the "OR" should receive the same marks as the preceding part it refers to.
For example, if part c is worth 2 marks, and an "OR" is provided for part d, the solution for part d should also receive 2 marks, aligning it with part c.
-The "OR" typically presents alternative solutions for the same question. So, both parts before and after the "OR" are conceptually tied to the same overall problem.
-Mention the question id in this format "question_id_38" do not make a separate key for the question id 
-Make sure the <image_id> if present is mentioned in the key "question_id_38" and in the question_image_description.
-No Hallucinations: Do not add, complete, rephrase, or interpret any part of the question or answer. Extract word-for-word from the PDF. Don’t use your own knowledge. Just copy exactly what’s written.
-No Redundancy:
If the main question contains shared instructions or diagrams which is a part of a sub-question, do not repeat them in sub-question.
Only include specific subquestion prompts in question_id_XX_A, XX_i, etc.
-Subquestion Logic:
Only create subquestions if they exist in the structure (like A, B, (i), etc.).
If there's only one question and answer, do not wrap it in a subquestions list.
-Diagrams:
Use <image_1>, <image_2>, etc., to reference diagrams.
Place them in question_id_description and diagram_description as applicable.
-Marking:
Use "solution_full_marks" for total marks at the main level.
-Use "marks_of_solution_XX" for each subpart.
OR-Based Questions:
If a question has Option A OR B, include both under subquestions.
Clean Output:
-Strip out all irrelevant headers, footers, page numbers, and line breaks.
Output Rules
Return only the final JSON array
No markdown
No commentary
No extra formatting
Fully machine-readable and clean text