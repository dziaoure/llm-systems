# Prompt Patterns (LLM Systems)

## 1. System Prompt (Policy + Role)
- Define: who the assisstent is, what it must di, and what it must avoid
- Keep it stable and versioned


## 2. Context Injecton (Grounding)
- Provide retrieved chunks / document text
- Use clear delimiters:
  - ---BEGIN CONTEXT---
  - ---END CONTEXT---


## 3. Task Prompt (User)
- Make output requirements explicit:
   - format (JSON, bullets, table)
   - fields and constraints


## 4. Strutured Outout (JSON)
- Ask for valid JSON only
- Include a JSON schema or explicit field list
- Add 'if unknown, set null


## 5. Anti-hallucination Guardrails
- 'Only use provided context.'
- 'If not in context, say you don't know'
- 'Cite chunk ids'


## 6. Self-check / Criticism Loop (Optional)
- Draft asnwer
- Verify against constrainta
- Output final