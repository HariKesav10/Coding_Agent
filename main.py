from Coder_Agent import CoderAgent
from prompts import SYSTEM_PROMPT, ERROR_CORRECTION_PROMPT
from python_orchestrator import CodeSandbox, extract_code_blocks

def main():
    # Initialize your local model agent & docker sandbox orchestrator
    agent = CoderAgent(model_id="ornith-ai/Ornith-1.5-9B")
    sandbox = CodeSandbox(timeout_seconds=15)

    # user_task = "Write a Python script that generates a 5x5 Pascal's Triangle using NumPy and prints the matrix to terminal."

    messages = [{"role": "user","content": [{"type": "text", "text": f"{SYSTEM_PROMPT}"}]}]

    max_attempts = 25
    for attempt in range(1, max_attempts + 1):
        print(f"\n================ [ Attempt {attempt}/{max_attempts} ] ================")

        # 1. Generate code using your local PyTorch model
        response_text = agent.generate_code(messages)
        code_to_run = extract_code_blocks(response_text)

        print("\n--- Generated Code ---")
        print(code_to_run)

        # 2. Execute code in isolated Docker Sandbox
        result = sandbox.run_code(code_string=code_to_run)

        # 3. Check result & feedback loop
        if result["success"]:
            print("\n✅ Sandbox Execution Succeeded!")
            print("--- Terminal Output ---")
            print(result["output"])
            break
        else:
            print("\n❌ Sandbox Execution Failed!")
            print("--- Error Log ---")
            print(result["output"])

            # Feed terminal error back to the model for self-correction
            error_feedback = ERROR_CORRECTION_PROMPT + f"""
                The code that was executed: {code_to_run}
                The code failed execution inside the terminal with the following output:
                {result['output']}
                Please fix the bug and return the full updated Python code inside ```python ``` blocks."""

            # Append assistant response & error feedback to conversation
            messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": response_text}]
            })
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": error_feedback}]
            })


if __name__ == "__main__":
    main()