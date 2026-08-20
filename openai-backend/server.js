require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { OpenAI } = require('openai');

const app = express();
app.use(cors());
app.use(express.json());

const port = process.env.PORT || 3000;
const openaiKey = process.env.OPENAI_API_KEY;
if (!openaiKey) {
  console.warn('Warning: OPENAI_API_KEY is not set. The /api endpoints will fail without it.');
}

const client = new OpenAI({ apiKey: openaiKey });

// Simple health check
app.get('/api/health', (req, res) => res.json({ ok: true }));

// Generate code/completion from a prompt
app.post('/api/generate-code', async (req, res) => {
  try {
    const prompt = req.body.prompt;
    if (!prompt || typeof prompt !== 'string') {
      return res.status(400).json({ error: 'prompt (string) is required in request body' });
    }

    const model = req.body.model || 'gpt-4o-code';
    // Call OpenAI Chat Completions (chat-style)
    const response = await client.chat.completions.create({
      model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: req.body.max_tokens || 800,
      temperature: typeof req.body.temperature === 'number' ? req.body.temperature : 0.2
    });

    const output = response?.choices?.[0]?.message?.content ?? '';
    res.json({ output });
  } catch (err) {
    console.error('OpenAI error', err);
    // Return sanitized error message
    res.status(500).json({ error: err?.message || 'OpenAI request failed' });
  }
});

app.listen(port, () => {
  console.log(`SPM OpenAI backend listening on http://localhost:${port}`);
});
