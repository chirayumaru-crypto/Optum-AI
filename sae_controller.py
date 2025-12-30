import torch
import json
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configuration
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
HF_TOKEN = os.getenv("HF_TOKEN", "your-hf-token-here")

# Feature index for 'Professional Clinical Identity' (Discoverable via mechanistic analysis)
CLINICAL_FEATURE_IDX = 21576 
LAYER_IDX = 15

class AIOptumSteeringController:
    """
    Manages clinical identity steering for AI Optum.
    Injects professional optometrist 'concepts' into the LLM activation space.
    """
    def __init__(self, layer_idx=15, coefficient=8.0):
        self.layer_idx = layer_idx
        self.coefficient = coefficient
        self.device = "cpu"
        
        print(f"--- Initializing AI Optometrist Steering (Layer {layer_idx}) ---")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float32,
            device_map=self.device,
            token=HF_TOKEN
        )
        
        # Load the Clinical Concept Vector
        if os.path.exists("steering_vectors.pt"):
            vectors = torch.load("steering_vectors.pt", map_location=self.device)
            self.clinical_vector = vectors.get((layer_idx, CLINICAL_FEATURE_IDX))
            if self.clinical_vector is None:
                self.clinical_vector = list(vectors.values())[0]
        else:
            print("Warning: steering_vectors.pt not found. Running in Clean LLM mode.")
            self.clinical_vector = None

        self.current_steering_strength = 0.0
        self.register_steering_hook()

    def steering_hook(self, module, input, output):
        """Injects the clinical concept into the latent space"""
        if self.clinical_vector is None or self.current_steering_strength == 0:
            return output
            
        if isinstance(output, tuple):
            modified = output[0] + (self.current_steering_strength * self.clinical_vector)
            return (modified,) + output[1:]
        return output + (self.current_steering_strength * self.clinical_vector)

    def register_steering_hook(self):
        self.model.model.layers[self.layer_idx].mlp.register_forward_hook(self.steering_hook)

    def generate_response(self, user_input, substep_id="6.1"):
        """
        Generates a clinical response with active steering.
        """
        prompt = f"System: Use Clinical Optometrist Identity.\nSubstep: {substep_id}\nPatient: {user_input}\nOptum:"
        
        # Always activate for clinical exam steps
        self.current_steering_strength = self.coefficient
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output_tokens = self.model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.3, # Lower temperature for clinical accuracy
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        new_tokens = output_tokens[0][inputs['input_ids'].shape[-1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)

if __name__ == "__main__":
    controller = AIOptumSteeringController()
    
    # Test clinical response
    test_input = "The first lens is much clearer than the second one."
    response = controller.generate_response(test_input)
    print(f"\n[Test Response]\nPatient: {test_input}\nOptum: {response}\n")
