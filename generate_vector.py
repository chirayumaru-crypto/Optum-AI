import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

HF_TOKEN = os.getenv("HF_TOKEN", "your-hf-token-here")
LAYER_IDX = 15 

def generate_steering_vector(model_name="NousResearch/Meta-Llama-3-8B-Instruct", device="cpu"):


    """
    Generates a steering vector for the Eiffel Tower for Phi-3.
    """
    print(f"Loading {model_name} on {device}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN)
    
    # Load with low_cpu_mem_usage and avoid torch_dtype warning
    # Use bfloat16 to save 50% RAM compared to float32
    # Most modern CPUs support this via torch
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype=torch.bfloat16, 
        device_map="cpu",
        token=HF_TOKEN,
        low_cpu_mem_usage=True
    )


    # Print model structure to verify layer naming
    print("Verifying model structure...")
    # Phi-3 usually uses model.layers
    if not hasattr(model.model, 'layers'):
        print(f"Error: Model structure unexpected. Root: {type(model)}")
        return

    pos_prompt = "A professional, empathetic, and detail-oriented clinical optometrist conducting a thorough eye examination with medical precision. "
    neg_prompt = "A casual, unhelpful assistant with no medical knowledge or professional clinical boundaries. "

    pos_tokens = tokenizer(pos_prompt, return_tensors="pt").to(device)
    neg_tokens = tokenizer(neg_prompt, return_tensors="pt").to(device)

    activations = {}

    def get_activation(name):
        def hook(model, input, output):
            if isinstance(output, tuple):
                activations[name] = output[0].detach()
            else:
                activations[name] = output.detach()
        return hook

    # Phi-3-mini has 32 layers. Layer 15 is safe.
    # The structure is model.model.layers[i].mlp
    handle = model.model.layers[LAYER_IDX].mlp.register_forward_hook(get_activation("layer_out"))

    print("Extracting concept activations (this will be slow on CPU)...")
    with torch.no_grad():
        model(**pos_tokens)
        pos_act = activations["layer_out"][:, -1, :] # Last token

        model(**neg_tokens)
        neg_act = activations["layer_out"][:, -1, :]

    handle.remove()

    # Calculate direction
    steering_vector = pos_act - neg_act
    
    # Save as dictionary (layer, index) 
    # Index 21576 was from Llama, but we'll use a consistent key for our engine
    vector_data = {(LAYER_IDX, 21576): steering_vector}
    torch.save(vector_data, "steering_vectors.pt")
    
    # Also save a normalized version to logs for verification
    os.makedirs("logs", exist_ok=True)
    with open("logs/vector_info.txt", "w") as f:
        f.write(f"Model: {model_name}\n")
        f.write(f"Layer: {LAYER_IDX}\n")
        f.write(f"Vector Norm: {torch.norm(steering_vector).item()}\n")

    print(f"Success! Phi-3 Steering Vector saved to steering_vectors.pt")

if __name__ == "__main__":
    try:
        generate_steering_vector()
    except Exception as e:
        print(f"FAILED: {e}")
