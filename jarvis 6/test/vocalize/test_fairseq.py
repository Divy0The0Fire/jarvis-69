import torch
from fairseq.models.wav2vec import Wav2Vec2Model
from os import environ

environ["TF_ENABLE_ONEDNN_OPTS"]="0"


# Load the model
model_path = 'wav2vec_large.pt'
model = Wav2Vec2Model.from_pretrained(model_path)
model.eval()
