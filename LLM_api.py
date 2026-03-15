# ─── LLM: DeepSeek via API ───────────────────────────────────────────────────

class QwenLLM:
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model  # "deepseek-chat" or "deepseek-reasoner"
        self.system_prompt = system_prompt
        self.history = []

    def chat(self, user_msg: str) -> str:
        # Build messages list (no manual prompt formatting needed)
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.history
        messages.append({"role": "user", "content": user_msg})

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                top_p=0.9,
                max_tokens=256,
            )
            answer = resp.choices[0].message.content.strip()

        except Exception as e:
            log.error(f"LLM error: {e}")
            answer = "I encountered an error processing your request."

        # Update history (same as before)
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": answer})
        if len(self.history) > CONFIG["max_history"] * 2:
            self.history = self.history[-CONFIG["max_history"] * 2:]

        return answer

    def reset(self):
        self.history = []