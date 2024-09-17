from flask import Flask, jsonify, request
import json
import pandas as pd
from tqdm import tqdm
from flask_cors import cross_origin

from transformers import BertTokenizer, BertModel
import torch
import os




tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()




def get_bert_embedding(text):
    # Tokenize input text and convert to PyTorch tensors
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the embeddings for the [CLS] token
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze()
    return embeddings




app = Flask(__name__)



print("Loding Self Learning (non-certified) Courses")
self_learning_path = "./db/"
self_learning_courses = dict()
self_learning_courses_embedding_map = dict()
self_learning_courses_links = dict()