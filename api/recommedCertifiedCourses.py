


#PANDAS NUMPY
import pandas as pd

#TQDM, AND UTILS
import time
from tqdm import tqdm
import random
import os

#FLASK PART
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json
app = Flask(__name__)


#BERT PART
from transformers import BertTokenizer, BertModel
import torch
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()


#postgresql part
import psycopg2
#!pip install psycopg2


class POSTGRESQL:
    def __init__(self, host, db, user, password, port):
        self.conn = psycopg2.connect(host=host,database=db,user=user,password=password,port=port)
    def command(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        results =cur.fetchall()
        cur.close()
        del cur
        return results
    def close(self):
        self.conn.close()



#get saved embeddings of all sectors
def get_embedding_vector_all_NSDC_sectors(NSDC_sectors_embeddings_path):
    NSDC_ALL_SECTOR_NAMES = []
    NSDC_ALL_SECTORS_EMBEDDINGS = dict()
    NSDC_sectors = pd.read_csv(NSDC_sectors_embeddings_path)
    for i in range(NSDC_sectors.shape[0]):
        s_name = NSDC_sectors['SECTOR_NAME'].iloc[i]
        emb_path = NSDC_sectors['EMBEDDING_PATH'].iloc[i]
        embedding_tensor = torch.load(emb_path)
        NSDC_ALL_SECTOR_NAMES.append(s_name)
        NSDC_ALL_SECTORS_EMBEDDINGS[s_name] = embedding_tensor
    return NSDC_ALL_SECTOR_NAMES, NSDC_ALL_SECTORS_EMBEDDINGS
NSDC_sectors_embeddings_path = "./utils/embeddings/NSDC_sectors/NSDC_sectors_metadata.csv"
NSDC_ALL_SECTOR_NAMES, NSDC_ALL_SECTORS_EMBEDDINGS = get_embedding_vector_all_NSDC_sectors(NSDC_sectors_embeddings_path)

def get_bert_embedding(text):
    # Tokenize input text and convert to PyTorch tensors
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the embeddings for the [CLS] token
    embeddings = outputs.last_hidden_state[:, 0, :].squeeze()
    return embeddings


def find_closest_key(query_embedding, embeddings):
    max_similarity = -1  # Initialize to a low value
    closest_key = None

    for key, embedding in embeddings.items():
        # Calculate cosine similarity
        similarity = torch.nn.functional.cosine_similarity(query_embedding.unsqueeze(0), embedding.unsqueeze(0))
        
        # Update closest key if the current similarity is greater
        if similarity > max_similarity:
            max_similarity = similarity
            closest_key = key

    return closest_key

def nearest_match_NSDC_sector(key):
    query_embedding = get_bert_embedding(key)
    closest_key = find_closest_key(query_embedding, NSDC_ALL_SECTORS_EMBEDDINGS)
    return closest_key


## Self Learning COURSES PARAMTERS
CC_sector_column_name = "sector"
CC_course_column_name = "name of course"
CC_video_title_column_name = "Video Title"
CC_video_link_column_name ="video_link_to_embed"
# CC_course_rating_column_name = "Rate this course out of 5 (where 1 is least and 5 is highest)"
# CC_basic_advanced_column_name = "Is this course a basic/ intermediate or advanced course?"
# CC_link_playing_column_name = "Is link playing?(Yes/No)"
# CC_video_relevance_column_name = "Is the video relevant to the course?(Yes/No)"
CC_courses_table_name = "CertifiedCoursesVideo"


app = Flask(__name__)



def getData_SL_courses(how='postgresql'):
    columns = [CC_sector_column_name, CC_course_column_name, CC_video_title_column_name, CC_video_link_column_name ]
    if how == 'postgresql':
        host="13.51.139.148"
        database="jksdm"
        user="umaid"
        password="wordpass"
        port=5432
        table_name= CC_courses_table_name
        postgresql_obj = POSTGRESQL(host,database,user,password,port)
        # # Fetch all table and column names
        # table_columns = postgresql_obj.command("""SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;""")


        # # Display table and column names
        # print("Tables and their columns:")
        # current_table = None
        # for table, column in table_columns:
        #     if table != current_table:
        #         print(f"\nTable: {table}")
        #         current_table = table
        #     print(f" - Column: {column}")
        # postgresql_obj.close()
        string = ""
        for c in columns:
            string += "\""+c+"\","
        #print(string[0:-1])
        #column_names = '"sector", "name of course", "Video Title", "video_link_to_embed", "Rate this course out of 5 (where 1 is least and 5 is highest)", "Is this course a basic/ intermediate or advanced course?", "Is link playing?(Yes/No)", "Is the video relevant to the course?(Yes/No)"'
        column_names = string[0:-1]       
        query = "SELECT " + column_names + " FROM " + '"'+table_name+'"'
        results = postgresql_obj.command(query)
        data_SL_courses = pd.DataFrame(results, columns = columns)
        postgresql_obj.close()
        return data_SL_courses
    
    else:
        file_path_to_load_SL_courses = "../db/UAT-SectorSkillVideosMerged.csv"
        data_from_csv = pd.read_csv(file_path_to_load_SL_courses)
        data_SL_courses = data_from_csv[columns]
        return data_SL_courses
    


import json


def get_sector_wise_basic_advanced_SL_courses(SL_courses_df):
    SL_courses_df_filtered = SL_courses_df[SL_courses_df[SL_basic_advanced_column_name]!=''] #non-empty Basic/Advanced Property
    sectors = list(SL_courses_df_filtered[SL_sector_column_name].unique())       
    print('STRUCTURING THE COURSES INTO BASIC AND ADVANCED TYPES')
    SL_BASIC_ADVANCED_MAPPING = dict()
    for sector in sectors:
        SL_BASIC_ADVANCED_MAPPING[sector]= {'BASIC':[], 'ADVANCED':[]}
        SL_sectored_videos = SL_courses_df_filtered[SL_courses_df_filtered[SL_sector_column_name]== sector]
        SL_courses_names_in_a_sector = list(SL_sectored_videos[SL_course_column_name].unique())
        for course in SL_courses_names_in_a_sector:
            SL_coursed_videos = SL_sectored_videos[SL_sectored_videos[SL_course_column_name]== course]
            all_videos_in_the_SL_course = SL_coursed_videos[[SL_video_title_column_name,SL_video_link_column_name]].values.tolist()
            
            basic_or_advanced_value_of_the_course = SL_coursed_videos[SL_basic_advanced_column_name].sample(1).iloc[0]
            #print(course,basic_or_advanced_value_of_the_course)
            
            
            
            if str(basic_or_advanced_value_of_the_course).lower() == 'basic':
                SL_BASIC_ADVANCED_MAPPING[sector]['BASIC'].append({'SL_course_title':course, 'SL_videos_in_course':all_videos_in_the_SL_course})
            if str(basic_or_advanced_value_of_the_course).lower() == 'advanced' or str(basic_or_advanced_value_of_the_course).lower() == 'intermediate':
                SL_BASIC_ADVANCED_MAPPING[sector]['ADVANCED'].append({'SL_course_title':course, 'SL_videos_in_course':all_videos_in_the_SL_course})
    
    #AI rated courses
    with open("../db/AI_UAT_SL_courses.json", "r") as file:
        SL_BASIC_ADVANCED_MAPPING.update(json.load(file))      
#     for s in SL_BASIC_ADVANCED_MAPPING.keys():
#         print('#######\nSectorName:- ',s, '; Basic.Courses:-',len(SL_BASIC_ADVANCED_MAPPING[s]['BASIC']) , '; Advanced.Courses:-',len(SL_BASIC_ADVANCED_MAPPING[s]['ADVANCED']),end='')
        
#         summa = 0
#         for c_idx in range(len(SL_BASIC_ADVANCED_MAPPING[s]['BASIC'])):
#             summa += len(SL_BASIC_ADVANCED_MAPPING[s]['BASIC'][c_idx]['SL_videos_in_course'])
#         print('; Basic.Videos:-', summa, end='')
#         summa = 0
#         for c_idx in range(len(SL_BASIC_ADVANCED_MAPPING[s]['ADVANCED'])):
#             summa += len(SL_BASIC_ADVANCED_MAPPING[s]['ADVANCED'][c_idx]['SL_videos_in_course'])
#         print('; Advanced.Videos:-', summa, end='')
        
       
    return SL_BASIC_ADVANCED_MAPPING



data_SL_courses = getData_SL_courses(how='csv')
#The following can be used to filter the available links and relevant links ONLY
data_SL_courses = data_SL_courses[(data_SL_courses[SL_link_playing_column_name] =='Yes')&(data_SL_courses[SL_video_relevance_column_name] =='Yes')]


#GET THE BASIC ADVANCED MAPPING
SL_BASIC_ADVANCED_MAPPING = get_sector_wise_basic_advanced_SL_courses(data_SL_courses)


# Route for the root URL
@app.route("/api/v2/2",  methods=['GET'])
@cross_origin()
def home():
    return f"<h2>Welcome to the JKYSE API for Self Learning Videos!</h2><br></h2>"


@app.route('/api/v1/RecommendSelfLearningCoursesAfterPsychometry', methods=['POST'])
@cross_origin()
def recommendSLCoursesAfterPsychometry():
    #sectors_and_marks =  json.loads(request.args.get("sectors", "[\"IT-ITes\":\"0.5\"]"))
    sectors_and_marks = request.get_json()
    #sort the keys
    sorted_sectors = sorted(sectors_and_marks, key=sectors_and_marks.get, reverse=True)
    #mapping_sector_to_type_of_course = dict()
    RESULTANT_COURSES = []
    HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR = 5
    for s in sorted_sectors:
        marks_in_sector = sectors_and_marks[s]
        recommend_for = 'BASIC'
        if marks_in_sector >=0.5:
            print('advanced recommended')
            recommend_for = 'ADVANCED'
        else:
            print('basic recommened')
            recommend_for = 'BASIC'
        

        #for (sector_name, marks) in sectors_and_marks.items():
        sector_name = s
        if sector_name not in list(SL_BASIC_ADVANCED_MAPPING.keys()):
            sector_name = nearest_match_NSDC_sector(sector_name)
        
        if len(SL_BASIC_ADVANCED_MAPPING[sector_name][recommend_for]) < HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR:
            HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR = len(SL_BASIC_ADVANCED_MAPPING[sector_name][recommend_for])
        
        #FIND CLOSEST MATCH TO SECTOR sector_name CALL IT sector_name2 AND USE sector_name2 BELOW
        #
        if sector_name not in list(SL_BASIC_ADVANCED_MAPPING.keys()):
            sector_name = nearest_match_NSDC_sector(sector_name)
        #print(sector_name)
        #print(SL_BASIC_ADVANCED_MAPPING[sector_name], recommend_for)
       
        RESULTANT_COURSES.append([SL_BASIC_ADVANCED_MAPPING[sector_name][recommend_for][:HOW_MANY_COURSES_TO_RECOMMEND_IN_EACH_SECTOR]])
        #print(sectors_and_marks, type(sectors_and_marks))
    #print(RESULTANT_COURSES)
    return RESULTANT_COURSES

    
    
    
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
