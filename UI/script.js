        





function startAssessment() {
    document.getElementById("loading").style.display ='block';
    sendAJAXRequest();
}

QA = {}
var num_questions_per_sector = 2;

function nextQuestion(questionNumber) {
    //alert(questionNumber-1);
    //alert(this.QA[questionNumber-1].option_id_selected);
    //alert(this.QA[questionNumber-1].option_id_selected);
    // if (this.QA[questionNumber-1].option_id_selected == "")
    // {
    //     alert('Choose an option and then click next!');
    //     return;
    // }
    // Hide all question sliders
    const questions = document.querySelectorAll('.question-slider');
    questions.forEach(question => question.style.display = 'none');

    // Show the selected question slider
    const question = document.getElementById('question-' + questionNumber);
    if (question) {
        question.style.display = 'block';
    }
    else
    {
        completeAssessment()
    }
}

function completeAssessment() {
    // Collect selected options
    // const teamworkSelection = document.querySelector('#question-1 .selected');
    // const entrepreneurshipInterestSelection = document.querySelector('#question-2 .selected');
    // const technicalSkillsSelection = document.querySelector('#question-3 .selected');

    // console.log(`Teamwork: ${teamworkSelection ? teamworkSelection.textContent : 'Not Selected'}`);
    // console.log(`Entrepreneurship Interest: ${entrepreneurshipInterestSelection ? entrepreneurshipInterestSelection.textContent : 'Not Selected'}`);
    // console.log(`Technical Skills: ${technicalSkillsSelection ? technicalSkillsSelection.textContent : 'Not Selected'}`);
    for (sector in this.QA){
        SECTORS_EVALUATED[sector]=0;
        for (question in this.QA[sector]){
            if(this.QA[sector][question]['option_id_selected'] == this.QA[sector][question]['option_id_correct']){
                SECTORS_EVALUATED[sector] += 1;
            }
        }
    
    //save_to_cookie(SECTORS_EVALUATED);
    }
    for (sector in this.QA){
        SECTORS_EVALUATED[sector]=SECTORS_EVALUATED[sector]/num_questions_per_sector;    
    //save_to_cookie(SECTORS_EVALUATED);
    }

    // console.log(SECTORS_EVALUATED);
    // console.log(this.QA);
    // Hide the psychometric section and show the hero section
    document.getElementById("psychometric-section").style.display = "none";
    document.getElementById("hero").style.display = "block";
    generatecharts();
    
    let sortedKeysDesc = Object.keys(SECTORS_EVALUATED).sort((a, b) => SECTORS_EVALUATED[b] - SECTORS_EVALUATED[a]);
    //console.log(SECTORS_EVALUATED); // Output: ['key2', 'key4', 'key1', 'key3']
    //console.log(sortedKeysDesc); // Output: ['key2', 'key4', 'key1', 'key3']


    

}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => section.style.display = 'none');

    // Show the selected section
    document.getElementById(sectionId).style.display = 'block';

    
    if(sectionId=='courses'){
        for(kn=0;kn<sectorsSelected.length;kn++){
            sendRecommendationRequestCourses(sectorsSelected[kn]);
            sendRecommendationRequestCertifiedCourses(sectorsSelected[kn])
        }
        sendRecommendationRequestCourses(qualificationSelected);
        sendRecommendationRequestCertifiedCourses(qualificationSelected);
        
        
    }
    
}




var response = {}



function sendAJAXRequest() {
    var xhr = new XMLHttpRequest();
    var url = "http://127.0.0.1:5000/api/v1/questionBank";
    var params = "sectors=" +JSON.stringify(sectorsSelected) + "&numQuestionsInEachSector="+num_questions_per_sector;
    
    xhr.open("GET", url +"?"+params);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseQuestionBank(xhr.status, xhr.responseText);
    };


    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseQuestionBank(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseQuestionBank(xhr.status, xhr.responseText);
        }
    };

    
    // Send the request
    xhr.send();
}


function sendRecommendationRequestCourses(name_of_match) {
    var xhr = new XMLHttpRequest();
    //http://127.0.0.1:5000/api/v1/RecommendCoursesBasedOnCareerChosen?career_name=industry
    var url = "http://127.0.0.1:5000/api/v1/RecommendCoursesBasedOnCareerChosen";
    var params = "career_name=" +JSON.stringify(name_of_match);
    xhr.open("GET", url +"?"+params);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseRecommendedCourses(xhr.status, xhr.responseText);
    };
    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseRecommendedCourses(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseRecommendedCourses(xhr.status, xhr.responseText);
        }
    };
    xhr.send();
}



function parseRecommendedCourses(responseStatus, responseText)
{
    responseDictCourses= JSON.parse(responseText)
    if (responseStatus != 200) //error has occured during fetching
    {
        alert('Error occurred! Try again. Error Code:'+responseStatus+ '. Error Details:'+responseText);
        return;
    }
    
    if (responseDictCourses.status=="fail")
        {
            alert('Error occurred! Try again. Error Details:'+responseDictCourses.message);
            //document.getElementById("intro-section").style.display = "block";
            //document.getElementById("psychometric-section").style.display = "none";
            return;
        }

    //parse all questions
        

    recommendedCoursesSection = document.getElementById('recommendedCoursesSection');

    for(kkk=0; kkk<responseDictCourses.courses_links.length; kkk++)
    {
        course_name = responseDictCourses.courses_recommended[kkk];
        if (course_name.length>10)
        {
            course_name = course_name.substring(0, 20)+"...";
        }
        course_link = responseDictCourses.courses_links[kkk];
        embed_link = course_link.replace("/watch?v=", "/embed/");
        recommendedCoursesSection.innerHTML += "<div class='tile'><iframe width='560' height='315' src='"+embed_link +"' title='"+course_name +"' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' allowfullscreen></iframe><a href='"+course_link+"' target='_blank'> <h2 class='clickable'>"+course_name +"</h2></a></div>";
    }

    //console.log(responseDict.message);
    //responseDict.message.forEach(sectorquestions => {
    //    console.log(sectorquestions.sector);
    //});

 }






 function sendRecommendationRequestCertifiedCourses(name_of_match) {
    var xhr = new XMLHttpRequest();
    //http://127.0.0.1:5000/api/v1/RecommendCoursesBasedOnCareerChosen?career_name=industry
    var url = "http://127.0.0.1:5002/api/v1/RecommendCertifiedCoursesBasedOnCareerChosen";
    var params = "career_name=" +JSON.stringify(name_of_match);
    xhr.open("GET", url +"?"+params);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseRecommendedCertifiedCourses(xhr.status, xhr.responseText);
    };
    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseRecommendedCertifiedCourses(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseRecommendedCertifiedCourses(xhr.status, xhr.responseText);
        }
    };
    xhr.send();
}



function parseRecommendedCertifiedCourses(responseStatus, responseText)
{
    responseDictCertifiedCourses= JSON.parse(responseText)
    if (responseStatus != 200) //error has occured during fetching
    {
        alert('Error occurred! Try again. Error Code:'+responseStatus+ '. Error Details:'+responseText);
        return;
    }
    
    if (responseDictCertifiedCourses.status=="fail")
        {
            alert('Error occurred! Try again. Error Details:'+responseDictCourses.message);
            //document.getElementById("intro-section").style.display = "block";
            //document.getElementById("psychometric-section").style.display = "none";
            return;
        }

    //parse all questions
        

    recommendedCertifiedCoursesSection = document.getElementById('recommendedCertifiedCoursesSection');

    for(kkk=0; kkk<responseDictCertifiedCourses.courses_links.length; kkk++)
    {
        course_name = responseDictCertifiedCourses.courses_recommended[kkk];
        if (course_name.length>10)
        {
            course_name = course_name.substring(0, 20)+"...";
        }
        course_link = responseDictCertifiedCourses.courses_links[kkk];
        recommendedCertifiedCoursesSection.innerHTML += "<div class='tile'><img src='download.jpg' style='width:250px; height:200px;' /><a href='"+course_link+"' target='_blank'> <h2 class='clickable' style='border:1px solid #000; padding:5px;'>"+course_name +"</h2></a></div>";
    }

    //console.log(responseDict.message);
    //responseDict.message.forEach(sectorquestions => {
    //    console.log(sectorquestions.sector);
    //});

 }

function chooseOption(sector_name,question_number,question_id,selected_option_id)

{
    // this.QA[x]['sector_name'] = sector_name;
    // this.QA[x]['question_id'] = question_id;
    // this.QA[]['option_id_selected'] = z;
    // this.QA[x]['option_id_correct'] = '';
    //QA['Capital Goods']['Q/2/ID1726559635062084497']['option_id_selected']
    // console.log(QA);
    // console.log("******");
    // console.log(QA[sector_name]);
    // console.log("******");
    // console.log(QA[sector_name][question_id]);
    // console.log("******");
    // console.log(QA[sector_name][question_id]['option_id_selected']);
    //alert(QA[sector_name][question_id]["option_id_selected"]);
    QA[sector_name][question_id]["option_id_selected"]= selected_option_id;
    //alert(QA[sector_name][question_id]["option_id_selected"]);
    
}


function parseQuestionBank(responseStatus, responseText)
{
    responseDict = JSON.parse(responseText)

    if (responseStatus != 200) //error has occured during fetching
    {
        document.getElementById("intro-section").style.display = "block";
        document.getElementById("loading").style.display = "none";
        document.getElementById("psychometric-section").style.display = "none";
        alert('Error occurred! Try again. Error Code:'+responseStatus+ '. Error Details:'+responseText);
        return;
    }
    
    
    if (responseDict.status=="fail")
        {
            alert('Error occurred! Try again. Error Details:'+responseDict.message);
            document.getElementById("intro-section").style.display = "block";
            document.getElementById("psychometric-section").style.display = "none";
            return;
        }

    //parse all questions
        

    psychometricsection = document.getElementById('psychometric-section');
    //console.log(responseDict.message);
    //responseDict.message.forEach(sectorquestions => {
    //    console.log(sectorquestions.sector);
    //});

    //console.log(responseDict);


    // responseDict.message.forEach(selectedSector=> {
    //     console.log(selectedSector);
    //     console.log("***");


    // });
    document.getElementById("intro-section").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("psychometric-section").style.display = "block";
    qn_count = 1
    for(s=0; s<responseDict.message.length; s++)
    {
        sector_name = responseDict.message[s].sector
        this.QA[sector_name] = {};
        
        for (q=0; q<responseDict.message[s].data.length; q++)
        {
            htmltext = "";
            question_id = responseDict.message[s].data[q].question.id
            question_statement = responseDict.message[s].data[q].question.statement;
            if (qn_count==1)
            {
                htmltext += "<div class='question-slider' id='question-"+qn_count+"' style='display:block;'>";
            }
            else
            {
                htmltext += "<div class='question-slider' id='question-"+qn_count+"' style='display:none;'>";
            }
            htmltext += "<div class='question' data-value='"+question_id+"' ><p>"+ question_statement+"</p></div>";
            
            //Sector name = responseDict.message[s].sector
            //Question_object = responseDict.message[s].data[q].question (params, id, statement)
            //Question_params = responseDict.message[s].data[q].question.params
            //Question_id = responseDict.message[s].data[q].question.id
            //Question_statement = responseDict.message[s].data[q].question.statement
            
            
            this.QA[sector_name][question_id] = {};
            this.QA[sector_name][question_id]["option_id_selected"] = '';

            //Options_object for a question=//Question_id = responseDict.message[s].data[q].question.options (array of option objects)
            for(o=0; o<responseDict.message[s].data[q].question.options.length;o++)
            {
               
               //option_id  = responseDict.message[0].data[0].question.options[o].id
               //option_statement  = responseDict.message[0].data[0].question.options[o].statement
               option_id  = responseDict.message[s].data[q].question.options[o].id
               correct_option_id = responseDict.message[s].data[q].question.correct_option.id
               option_statement = responseDict.message[s].data[q].question.options[o].statement
               op_=o+1

               //functiontext = "<div class=\"option\" onclick=\"selectOption('teamwork', 'option"+op_+"')\">"+option_statement+"</div>";
               //console.log(functiontext);
               //selectionpair = "'"+question_id+"','"+option_id+"'";
               
               this.QA[sector_name][question_id]["option_id_correct"] = correct_option_id;
               
               //this.QA[qn_count]={}
               //this.QA[qn_count]['sector_name'] = sector_name;
               //this.QA[qn_count]['question_id'] = question_id;
               //this.QA[qn_count]['option_id_selected'] = '';
               //this.QA[qn_count]['option_id_correct'] = '';
               htmltext += "<div class='option' data-value='"+option_id+"' class=\"\" onclick=\"chooseOption('"+sector_name+"','"+qn_count+"','"+question_id+"','"+option_id+"')\">"+option_statement+"</div>";
               
            }
            qq = qn_count+1;
            htmltext +="<button id='nextbutton' onclick=\"nextQuestion("+qq+")\">Next</button></div>";
            psychometricsection.innerHTML +=htmltext;

            //correct_option object for a question = //Question_id = responseDict.message[s].data[q].question.correct_option (id, statement)
            //correct_option_id  a question = //Question_id = responseDict.message[s].data[q].question.correct_option.id
            //correct_option_statement = //Question_id = responseDict.message[s].data[q].question.correct_option.statement


            qn_count++;
        }
    }
    




    }
        


// document.addEventListener("DOMContentLoaded", function() {
//     // Attach event listeners to options
//     const options = document.querySelectorAll(".option");
//     options.forEach(option => {
//         option.addEventListener("click", function() {
//             // Remove 'selected' class from all options in the current question
//             this.parentNode.querySelectorAll(".option").forEach(opt => opt.classList.remove("selected"));


//             // Add 'selected' class to the clicked option
//             this.classList.add("selected");
//             alert('Hi');
            
//         });
//     });
// });

function generatecharts(){
            
    //SECTORS_EVALUATED= {"IT-ITeS":0.5,"HealthCare":0.6, "ABC":0.9}
    console.log("***SectorsEvaluated*****");
    console.log(SECTORS_EVALUATED);
    
    chartContainer = document.getElementById("chartContainer");
    charts_html= "";
    chart_number =0;

    colorPairs = {}
    colorPairs[1] = ["Red", "Black"];
    colorPairs[2] = ["Blue", "Green"];
    colorPairs[3] = ["Purple", "Lime"];
    colorPairs[4] = ["Cyan", "Black"];
    colorPairs[5] = ["Magenta", "Green"];
    
    for (sector in SECTORS_EVALUATED)
    {
        console.log('loop running')
        chart_number++;
        charts_html +=  "<div class='chart-wrapper'><canvas id='chart"+chart_number+"' aria-label='chart' height='350' width='350'></canvas></div>";
        
    }
    chartContainer.innerHTML = charts_html;
    //imputed chart divs in chartContainer
    
    chart_number =0;
    for (sector in this.SECTORS_EVALUATED)
    {
        loadcharts(++chart_number, sector, SECTORS_EVALUATED[sector]);

    }
    
    function loadcharts(chart_number, sector_name, marks_in_sector)
    {
       var chrt = document.getElementById("chart"+chart_number).getContext("2d");
       var chartId = new Chart(chrt, {
        type: 'doughnut',
        data: {
          labels: ["Correct", "Incorrect"],
          datasets: [{
            label: "",
            data: [marks_in_sector, (1 - marks_in_sector)],
            backgroundColor: colorPairs[chart_number],
            hoverOffset: 5
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,  // Set to false if you don't want the legend
              position: 'top'
            },
            tooltip: {
              enabled: true // Customize tooltips here
            },
            datalabels: {
              formatter: (value, ctx) => {
                let sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                let percentage = (value / sum * 100).toFixed(2) + "%";  // Calculate percentage
                return percentage;
              },
              color: '#fff', // Label color
              font: {
                weight: 'bold',
                size: 14  // Adjust font size
              },
              anchor: 'center',
              align: 'center'
            }
          },
          cutout: '50%',  // Adjust the doughnut hole size
        }
      });



    }
    
}



document.addEventListener("DOMContentLoaded", function() {
    // Attach the event listener to the parent container
    const parent = document.querySelector("#psychometric-section");

    // Use event delegation to handle clicks on dynamically added options
    parent.addEventListener("click", function(event) {
        // Check if the clicked element has the class 'option'
        if (event.target.classList.contains("option")) {
            // Remove 'selected' class from all options in the current question
            const options = event.target.parentNode.querySelectorAll(".option");
            options.forEach(option => option.classList.remove("selected"));

            // Add 'selected' class to the clicked option
            event.target.classList.add("selected");
        }
    });
});