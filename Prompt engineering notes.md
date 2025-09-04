# Prompt Engineering Notes

- **System prompt**: I set the assistant’s personality to be friendly and concise. By default it gives short, bulleted answers (top 3–5 items) and only asks clarifying questions if they’re really needed (like dates for packing). I also told it not to invent exact details (like prices) and to admit when unsure.

- **Router prompt**: I use a separate prompt that makes the model return only JSON with fields like intent, destination, date, preferences, etc. This keeps tool calls (weather, country info) predictable and avoids random text.

- **Answer prompt**: Here the model is allowed to “think step by step” internally but only output the final answer. This works best for tasks like picking destinations or suggesting what to pack. I guide it to use bullets, give quick rationales, and offer to expand if the user wants more detail.

- **Conciseness & control**: The combination of a strict router + hidden reasoning in the answer gives me both reliability (no hallucinated tools) and natural, helpful responses that don’t overwhelm the user.
