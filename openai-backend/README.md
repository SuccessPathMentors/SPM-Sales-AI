# SPM OpenAI Backend

This is a minimal Node.js/Express backend that forwards prompts to OpenAI and returns code/completions. Designed as a starting point for integrating Codex-style features into the SPM-Sales-AI repo.

Features
- /api/generate-code: POST { prompt, model? } -> { output }
- CORS enabled for local dev
- Uses official OpenAI Node client

Security
- Add your OpenAI API key to environment variable OPENAI_API_KEY
- Do NOT commit your API key

Development
1. Install dependencies

   npm install

2. Create a .env file based on .env.example

3. Run locally

   npm run dev

Request example

POST /api/generate-code
Content-Type: application/json

{
  "prompt": "Write a function in JavaScript that reverses a string",
  "model": "gpt-4o-code"
}

Response:

{
  "output": "function reverseString(s) { return s.split('').reverse().join(''); }"
}
