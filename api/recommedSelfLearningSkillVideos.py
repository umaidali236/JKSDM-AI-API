from flask import Flask, jsonify, request
import json
from transformers import BertTokenizer, BertModel
import torch
import os
from tqdm import tqdm
from flask_cors import cross_origin
app = Flask(__name__)





# Route for the root URL
@app.route("/")
@cross_origin()
def home():
    return f"<h2>Welcome to the JKYSE API for Self Learning Videos!</h2><br> Total sectors added to API </h2>"


@app.route('/api/v1/RecommendSelfLearningCoursesAfterPsychometry', methods=['POST'])
@cross_origin()
def recommendSLCoursesAfterPsychometry():
    
    #sectors_and_marks =  json.loads(request.args.get("sectors", "[\"IT-ITes\":\"0.5\"]"))
    sectors_and_marks = request.get_json()
    print(sectors_and_marks)
    return sectors_and_marks

    # Get the 'id' query parameter from the request
    # career_name = request.args.get('career_name', 'Computer Engineering')
    # career_score = float(request.args.get('career_score', '0.5'))
    
    # embedding_of_career_name = get_bert_embedding(career_name)
    # cosine_similarity_with_careers = dict()
    # for self_learning_career_name in list(self_learning_courses_embedding_map.keys()):
    #     cosine_similarity_with_careers[self_learning_career_name] = torch.nn.functional.cosine_similarity(embedding_of_career_name, self_learning_courses_embedding_map[self_learning_career_name], dim=0)
    
    # careers_data_sorted = {k: v for k, v in sorted(cosine_similarity_with_careers.items(), key=lambda x: x[1])}
    # careers_data_sorted_list = list(careers_data_sorted.keys())
    # CAREERS_DATA_SORTED = dict()
    # CAREERS_DATA_SORTED['status'] ='success'
    
    
    
    # CAREERS_DATA_SORTED['courses_recommended']= [careers_data_sorted_list[-kkk] for kkk in range(1, int(career_score*10))] 
    # CAREERS_DATA_SORTED['courses_links']= [self_learning_courses_links[careers_data_sorted_list[-kkk]] for kkk in range(1, int(career_score*10))]
    
    


    # return jsonify(CAREERS_DATA_SORTED) 




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5010,debug=True)
