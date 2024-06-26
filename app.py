import os
import torch
import torch.nn as nn
from collections import OrderedDict

def get_state_dict(shard_num, prefix=None):
    d = torch.load(os.path.join(model_path, f"pytorch_model_{shard_num:05d}-of-00072.bin"))
    return d if prefix is None else OrderedDict((k.replace(prefix, ''), v) for k, v in d.items())

from transformers import AutoTokenizer, AutoModelForCausalLM, BloomConfig
from transformers.models.bloom.modeling_bloom import BloomBlock, build_alibi_tensor

model_path = "/Volumes/Volume/bloom/new/bloom" # replace with your local folder path
config = BloomConfig.from_pretrained(model_path, local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
device = 'cpu'

def load_embeddings():
    state_dict = get_state_dict(shard_num=1, prefix="word_embeddings_layernorm.")
    embeddings = nn.Embedding.from_pretrained(state_dict.pop('word_embeddings.weight'))
    lnorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_epsilon, dtype=torch.bfloat16)
    lnorm.load_state_dict(state_dict)
    return embeddings.to(device), lnorm.to(device)

def load_causal_lm_head():
    linear = nn.utils.skip_init(
        nn.Linear, config.hidden_size, config.vocab_size, bias=False, dtype=torch.bfloat16)
    linear.load_state_dict(get_state_dict(shard_num=1, prefix="word_embeddings."), strict=False)
    return linear.bfloat16().to(device)

def load_block(block_obj, block_num):
    block_obj.load_state_dict(get_state_dict(shard_num=block_num + 2, prefix=f"h.{block_num}."))
    block_obj.to(device)

final_lnorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_epsilon, dtype=torch.bfloat16)
final_lnorm.load_state_dict(get_state_dict(shard_num=72, prefix="ln_f."))
final_lnorm.to(device)
block = BloomBlock(config, layer_number=1).bfloat16()

# run
device = 'cpu'
def forward(input_ids):
    # 1. Create attention mask and position encodings
    attention_mask = torch.ones(len(input_ids)).unsqueeze(0).bfloat16().to(device)
    alibi = build_alibi_tensor(input_ids.shape[1], config.num_attention_heads,
                               torch.bfloat16).to(device)
    # 2. Load and use word embeddings
    embeddings, lnorm = load_embeddings()
    hidden_states = lnorm(embeddings(input_ids))
    del embeddings, lnorm

    # 3. Load and use the BLOOM blocks sequentially
    for block_num in range(70):
        load_block(block, block_num)
        hidden_states = block(hidden_states, attention_mask=attention_mask, alibi=alibi)[0]
        print(".", end='')
    
    hidden_states = final_lnorm(hidden_states)
    
    #4. Load and use language model head
    lm_head = load_causal_lm_head()
    logits = lm_head(hidden_states)

    # 5. Compute next token 
    return torch.argmax(logits[:, -1, :], dim=-1)

input_sentence = "The SQL command to extract all the users whose name starts with A is: "
input_ids = tokenizer.encode(input_sentence, return_tensors='pt').to(device)
max_tokens = 10
for i in range(max_tokens): 
    print(f"Token {i + 1} ", end='')
    new_id = forward(input_ids)
    input_ids = torch.cat([input_ids, new_id.unsqueeze(-1)], dim=-1)
    print(tokenizer.decode(new_id))

print(tokenizer.decode(input_ids.squeeze(), skip_special_tokens=True))