import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig

class CoderAgent:
    def __init__(self, model_id: str = "ornith-ai/Ornith-1.5-9B"):
        print(f"Loading model {model_id} onto GPU")
        # qunatization=BitsAndBytesConfig(
        #    bnb_4bit_compute_dtype="auto",
        #     bnb_4bit_quant_type=
        # )
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForMultimodalLM.from_pretrained(
            model_id, 
            device_map="cuda:0",
            torch_dtype="auto",
            # quantization_config=qunatization
        )

    def generate_code(self, conversation_history: list) -> str:
        """
        Takes conversation history, applies model chat template, and returns generated text.
        """
        inputs = self.processor.apply_chat_template(
            conversation_history,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=200000,
                do_sample=False,
                temperature=0.0
            )

        # Decode output past the prompt token length
        input_len = inputs["input_ids"].shape[-1]
        response_text = self.processor.decode(outputs[0][input_len:], skip_special_tokens=True)
        return response_text