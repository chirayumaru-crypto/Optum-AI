import torch
import json
import os

class SAESteeringHook:
    def __init__(self, config, feature_vectors):
        """
        feature_vectors: Dict mapped by feature_id
        """
        self.config = config
        self.vectors = feature_vectors
        self.log_path = config['evaluation']['log_path']
        self.steering_enabled = config['steering']['enabled']
        self.layer_idx = config['layer_idx']
        
    def __call__(self, module, input, output):
        if isinstance(output, tuple):
            hidden_states = output[0]
        else:
            hidden_states = output

        steered_hidden = hidden_states

        if self.steering_enabled:
            # 1. Identity Steering (Dominant)
            id_cfg = self.config['steering_layers']['identity']
            id_vec = self.vectors[id_cfg['feature_id']].flatten().to(hidden_states.dtype)
            id_floor = id_cfg['alpha'] * id_vec
            steered_hidden = torch.max(steered_hidden, id_floor)

            # 2. Landmark Grounding (Supportive)
            lm_cfg = self.config['steering_layers']['landmark']
            lm_vec = self.vectors[lm_cfg['feature_id']].flatten().to(hidden_states.dtype)
            lm_floor = lm_cfg['alpha'] * lm_vec
            steered_hidden = torch.max(steered_hidden, lm_floor)

        # 3. Observation Logic (Log both features)
        log_data = {"layer": self.layer_idx, "timestamp": os.times()[4]}
        for name, cfg in self.config['steering_layers'].items():
            f_vec = self.vectors[cfg['feature_id']].flatten().to(steered_hidden.dtype)
            norm_sq = torch.norm(f_vec)**2
            act = (steered_hidden * f_vec).sum(dim=-1) / norm_sq
            log_data[f"{name}_activation"] = round(act[0, -1].item(), 4)


        self._log_activations(log_data)

        if isinstance(output, tuple):
            return (steered_hidden,) + output[1:]
        return steered_hidden

    def _log_activations(self, data):
        with open(self.log_path, "a") as f:
            f.write(json.dumps(data) + "\n")

