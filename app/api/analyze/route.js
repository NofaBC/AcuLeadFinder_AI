// app/api/analyze/route.js
import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { text, analysisType } = await request.json();

    if (!process.env.OPENROUTER_API_KEY) {
      return NextResponse.json(
        { error: 'OpenRouter API key not configured' },
        { status: 500 }
      );
    }

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://acu-lead-finder-ai.vercel.app',
        'X-Title': 'ACU Lead Finder AI'
      },
      body: JSON.stringify({
        model: 'openai/gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: `You are an expert lead analysis AI. Analyze the provided lead information and provide insights for ${analysisType || 'general lead qualification'}.`
          },
          {
            role: 'user',
            content: `Please analyze this lead information: ${text}`
          }
        ],
        max_tokens: 1000
      })
    });

    if (!response.ok) {
      throw new Error(`OpenRouter API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json({ 
      analysis: data.choices[0].message.content,
      usage: data.usage 
    });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to analyze lead' },
      { status: 500 }
    );
  }
}
