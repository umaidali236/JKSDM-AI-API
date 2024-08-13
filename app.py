from flask import Flask, jsonify, request
import json


app = Flask(__name__)



@app.route('/v1/StudentOptions', methods=['GET'])


def get_data():
    
     # Get the 'id' query parameter from the request
    qualification = request.args.get('qualification')
   
        # Load the JSON data
    with open('./json/StudentOptions/'+qualification+'.json') as f:
            data = json.load(f)
    # Retrieve data from the JSON file
    
    item = data.get(qualification)
        
    return jsonify(item)

    

@app.route('/v1/Exams')
        

def get_data_exams():

    subject_name=request.args.get('subject')
    
    with open('./json/Exams/'+subject_name+'.json') as f:
            data=json.load(f)
    item= data.get(subject_name)
    return jsonify(item)

@app.route('/v1/Courses',methods=['GET'])

def get_data_courses():
      
      course_name=request.args.get('course_name')

      with open('./json/Courses/'+course_name+'.json') as f:
            data=json.load(f)
      item=data.get(course_name)
      return jsonify(item)      


if __name__ == '__main__':
    app.run(debug=True)

        
    
    






