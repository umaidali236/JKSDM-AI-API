import pandas as pd
from transformers import BertTokenizer, BertModel
import torch

from tqdm import tqdm

from flask import Flask, jsonify, request
from flask_cors import cross_origin





app = Flask(__name__)




#import bert
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

ecourses = pd.read_csv('./db/CONTENT/E-courses.csv')





certified_e_courses_embedding_map = dict()
certified_learning_courses_links = dict()


def get_bert_embedding(text):
    # Tokenize input text and convert to PyTorch tensors
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get the embeddings for the [CLS] token
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze()
    return embeddings


ecoursesembeddings = dict()
certified_learning_courses_metadata = dict()

for i in tqdm(range(ecourses.shape[0])):
    sector_name = str(ecourses['Sector'].iloc[i])
    if sector_name == "nan":
        sector_name = " "
    course_name = str(ecourses['Name Of Course'].iloc[i])
    if course_name == "nan":
        course_name = " "
    
    link = str(ecourses['For Certification Advanced Module'].iloc[i])
    
    if not str(ecourses['Online'].iloc[i]) == "nan":
        paid_free =  str(ecourses['Online'].iloc[i])
    else:
        paid_free =  " "
    
    
    certified_e_courses_embedding_map[course_name] = get_bert_embedding(sector_name + " " + course_name)
    certified_learning_courses_links[course_name] = link
    certified_learning_courses_metadata[course_name] = {'Type':paid_free}




@app.route('/api/v1/RecommendCertifiedCoursesBasedOnCareerChosen', methods=['GET'])
@cross_origin()
def recommendCoursesOnCareer():
    # Get the 'id' query parameter from the request
    career_name = request.args.get('career_name')
    career_score = float(request.args.get('career_score', '0.5'))
    # cosine_similarity_with_sectors = dict()
    # embedding_of_sector_name = get_bert_embedding(sector_name)
    # embedding_of_career_name = get_bert_embedding(career_name)


    # for self_learning_sector_name in list(self_learning_courses.keys()):
    #     cosine_similarity_with_sectors[self_learning_sector_name] = torch.nn.functional.cosine_similarity(embedding_of_sector_name, self_learning_courses[self_learning_sector_name]['sector_embedding'], dim=0)

    # max_cosine_similarity_sector = -2
    # sector_name_with_max_cosine_similarity = 'Information Technology'

    # for (key, val) in cosine_similarity_with_sectors.items():
    #     #print(key,val)
    #     if val >= max_cosine_similarity_sector:
    #         sector_name_with_min_cosine_similarity = key
    #         max_cosine_similarity_sector = val
    embedding_of_career_name = get_bert_embedding(career_name)
    cosine_similarity_with_careers = dict()
    for certified_course_name in list(certified_e_courses_embedding_map.keys()):
        cosine_similarity_with_careers[certified_course_name] = torch.nn.functional.cosine_similarity(embedding_of_career_name, certified_e_courses_embedding_map[certified_course_name], dim=0)
    
    certified_courses_data_sorted = {k: v for k, v in sorted(cosine_similarity_with_careers.items(), key=lambda x: x[1])}
    certified_courses_data_sorted_list = list(certified_courses_data_sorted.keys())
    CERTIFIED_COURSES_DATA_SORTED = dict()
    CERTIFIED_COURSES_DATA_SORTED['status'] ='success'

    
    CERTIFIED_COURSES_DATA_SORTED['courses_recommended']= [certified_courses_data_sorted_list[-kkk] for kkk in range(1, int(career_score*10))]
    CERTIFIED_COURSES_DATA_SORTED['courses_links']= [certified_learning_courses_links[certified_courses_data_sorted_list[-kkk]] for kkk in range(1, int(career_score*10))]
    return jsonify(CERTIFIED_COURSES_DATA_SORTED)





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002,debug=True)

