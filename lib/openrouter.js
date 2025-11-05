export async function callOpenRouterAI(messages, model = 'meta-llama/llama-3.1-8b-instruct:free') {
    try {
        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.NEXT_PUBLIC_OPENROUTER_API_KEY}`,
                'HTTP-Referer': process.env.NEXT_PUBLIC_APP_URL,
                'X-Title': process.env.NEXT_PUBLIC_APP_NAME
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
                max_tokens: 1000
            })
        });

        if (!response.ok) {
            throw new Error(`OpenRouter API error: ${response.status}`);
        }

        const data = await response.json();
        return data.choices[0].message.content;
    } catch (error) {
        console.error('Error calling OpenRouter:', error);
        throw error;
    }
}
