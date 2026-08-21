import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit = True,
    bnb_4bit_quant_type= "nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_bits=8,
    low_mem_usage = True
)

device = "cuda" if torch.cuda.is_available else "cpu"

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen-2.5-",
    quantization_config=quantization_config,
    )