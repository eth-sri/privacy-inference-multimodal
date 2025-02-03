// ./app/api/chat/route.js
import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG_ID
});

export const runtime = 'edge';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const response = await openai.chat.completions.create({
    model: 'gpt-4-1106-preview',
    stream: true,
    temperature: 0,
    messages: [
      {'role': 'system', 'content': 'You are an expert investigator with years of experience in online profiling and text analysis. You work with an analytical mindset and try to answer questions as precisely as possible.'}, 
      ...messages
  ],
  });
  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
}