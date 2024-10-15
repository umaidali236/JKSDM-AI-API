
var base_url="http://127.0.0.1:5000";


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
        completeAssessment();
        showSection("recommendationSection");
    
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

// selected_languages=["Arabic","Japanese"]
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => section.style.display = 'none');

    // Show the selected section
    document.getElementById(sectionId).style.display = 'block';

    if(sectionId=='recommendationSection'){
        {
            sendRecommendationRequestSLCourses();
             sendRecommendationRequestCCCourses();
             sendRecommendationRequestDPR();
            //loadlistoncountry(selected_languages);
        }
        //sendRecommendationRequestSLCourses(qualificationSelected);
        //sendRecommendationRequestCertifiedCourses(qualificationSelected);
        
        
    }
    
}



var response = {}



function sendAJAXRequest() {
    var xhr = new XMLHttpRequest();
    var url = base_url+"/api/v1/questionBank";
    //var params = "sectors=" +JSON.stringify(sectorsSelected) + "&numQuestionsInEachSector="+num_questions_per_sector;
    var data = JSON.stringify({
        sectors: sectorsSelected,
        numQuestionsInEachSector: num_questions_per_sector
    });
    console.log(data);

    xhr.open("POST", url, true);
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
    xhr.send(data);
}

function sendRecommendationRequestSLCourses() {
    var xhr = new XMLHttpRequest();
    var url = base_url+"/api/v1/RecommendSelfLearningCoursesAfterPsychometry";
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseRecommendedSLCourses(xhr.status, xhr.responseText);
    };
    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseRecommendedSLCourses(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseRecommendedSLCourses(xhr.status, xhr.responseText);
        }
    };
    
    xhr.send(JSON.stringify(SECTORS_EVALUATED));
}

function parseRecommendedSLCourses(responseStatus, responseText)
{
    responseDictCourses= JSON.parse(responseText);
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
    recommendedCoursesSection = document.getElementById('recommendedCoursesSection');
    for(s=0; s<responseDictCourses.length; s++)
    {
        for(c=0; c<responseDictCourses[s][0].length; c++){
            course_name = responseDictCourses[s][0][c]['SL_course_title'];
            topic_num = 0
            topic_names = responseDictCourses[s][0][c]['SL_videos_in_course'][topic_num][0];
            topic_links = responseDictCourses[s][0][c]['SL_videos_in_course'][topic_num][1];
            embed_link = topic_links.replace("/watch?v=", "/embed/");
            recommendedCoursesSection.innerHTML += "<div class='tile'><iframe width='560' height='315' src='"+embed_link +"' title='"+course_name +"' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' allowfullscreen></iframe><a href='"+topic_links+"' target='_blank'> <h2 class='clickable'>"+course_name +"</h2></a></div>";
        }
        
    }
    //console.log(responseDictCourses)

}




function sendRecommendationRequestCCCourses() {
    var xhr = new XMLHttpRequest();
    var url = base_url+"/api/v1/RecommendCertifiedCoursesAfterPsychometry";
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseRecommendedCCCourses(xhr.status, xhr.responseText);
    };
    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseRecommendedCCCourses(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseRecommendedCCCourses(xhr.status, xhr.responseText);
        }
    };
    
    xhr.send(JSON.stringify(SECTORS_EVALUATED));
}

function parseRecommendedCCCourses(responseStatus, responseText)
{
    responseDictCCCourses= JSON.parse(responseText);
    if (responseStatus != 200) //error has occured during fetching
    {
        alert('Error occurred! Try again. Error Code:'+responseStatus+ '. Error Details:'+responseText);
        return;
    }
    
    if (responseDictCCCourses.status=="fail")
        {
            alert('Error occurred! Try again. Error Details:'+responseDictCCCourses.message);
            //document.getElementById("intro-section").style.display = "block";
            //document.getElementById("psychometric-section").style.display = "none";
            return;
        }
    recommendedCoursesSection = document.getElementById('recommendedCertifiedCoursesSection');
    for(s=0; s<responseDictCCCourses.length; s++)
    {
        for(c=0; c<responseDictCCCourses[s]['Course Details'].length; c++){
            course_name = responseDictCCCourses[s]['Course Details'][c]['CC_course_title'];
            topic_num = 0;
            course_description = responseDictCCCourses[s]['Course Details'][c]['CC_course_description'];
            course_link = responseDictCCCourses[s]['Course Details'][c]['CC_course_link'];
            
            recommendedCoursesSection.innerHTML += "<div class='tile'><a href='"+course_link+"' target='_blank'><img src='static/certified_courses_thumbnail.jpg' width='310' height='310' ><h2 class='clickable'>"+course_name +"</h2></a></div>";            
        }
        
    }
    //console.log(responseDictCourses)

}


function sendRecommendationRequestDPR() {
    var xhr = new XMLHttpRequest();
    var url = base_url+"/api/v1/RecommendDPRAfterPsychometry";
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseRecommendedDPR(xhr.status, xhr.responseText);
    };
    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseRecommendedDPR(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseRecommendedDPR(xhr.status, xhr.responseText);
        }
    };
    
    xhr.send(JSON.stringify(SECTORS_EVALUATED));
}

function parseRecommendedDPR(responseStatus, responseText)
{
    responseDictDPR= JSON.parse(responseText);
    if (responseStatus != 200) //error has occured during fetching
    {
        alert('Error occurred! Try again. Error Code:'+responseStatus+ '. Error Details:'+responseText);
        return;
    }
    
    if (responseDictDPR.status=="fail")
        {
            alert('Error occurred! Try again. Error Details:'+responseDictDPR.message);
            //document.getElementById("intro-section").style.display = "block";
            //document.getElementById("psychometric-section").style.display = "none";
            return;
        }
    recommendedDPRSection = document.getElementById('recommendedDPRSection');
    for(s=0; s<responseDictDPR.length; s++)
    {
        for(c=0; c<responseDictDPR[s]['DPR Details'].length; c++){
            dpr_name = responseDictDPR[s]['DPR Details'][c]['DPR_title'];
            dpr_link = responseDictDPR[s]['DPR Details'][c]['DPR_link'];
            recommendedDPRSection.innerHTML += "<div class='tile'><a href='"+dpr_link+"' target='_blank'><img src='static/dpr_thumbnail.jpg' width='310' height='310' ><h2 class='clickable'>"+dpr_name +"</h2></a></div>";
            
        }
        
    }

}


 function sendRecommendationRequestCertifiedCourses(name_of_match) {
    var xhr = new XMLHttpRequest();
    //http://127.0.0.1/api/v1/RecommendCoursesBasedOnCareerChosen?career_name=industry
    var url = base_url+":5002/api/v1/RecommendCertifiedCoursesBasedOnCareerChosen";
    
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
   
    // var params = "career_name=" +JSON.stringify(name_of_match);
    // xhr.open("GET", url +"?"+params);
    // xhr.setRequestHeader('Content-Type', 'application/json');
    
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
        
    
function loadlistoncountry(selected_languages) {
    var xhr = new XMLHttpRequest();
    var url = base_url+"/api/v1/recommend_languages";
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.timeout = 5000;

    xhr.ontimeout = function() {
        parseRecommendedlanguages(xhr.status, xhr.responseText);
    };
    error = 1
    // Set the onload callback function
    xhr.onload = function () {
        if (xhr.status == 200) {
            parseRecommendedlanguages(xhr.status, xhr.responseText);
        } 
        else 
        {
            parseRecommendedlanguages(xhr.status, xhr.responseText);
        }
    };
    var requestBody = {
        "interested_languages":selected_languages 
    };
    xhr.send(JSON.stringify(requestBody));
}
function parseRecommendedlanguages(responseStatus, responseText) {
    let responseDictlanguages = JSON.parse(responseText);
    
    if (responseStatus !== 200) { 
        alert('Error occurred! Try again. Error Code: ' + responseStatus + '. Error Details: ' + responseText);
        return;
    }
    // Check for recommendations in the response
    if (!responseDictlanguages.recommendations || responseDictlanguages.recommendations.length === 0) {
        alert('No recommendations found for the selected languages.');
        return;
    }
    recommendedlanguagesSection = document.getElementById('recommendedlanguagesSection');
    recommendedlanguagesSection.innerHTML = ''; 
    let lastLanguageName=null;
for (let c = 0; c < responseDictlanguages.recommendations.length; c++) {
    let language_name = responseDictlanguages.recommendations[c]['language'];
    let video_name = responseDictlanguages.recommendations[c]['video_name'];
    let video_link = responseDictlanguages.recommendations[c]['url'];
    let videoID = video_link.split('v=')[1]?.split('&')[0]; // Extracts the ID
    let embed_link = videoID ? `https://www.youtube.com/embed/${videoID}` : '';
    
     // Check if the language has changed
     if (language_name !== lastLanguageName) {
        // Close the previous language section if it's not the first language
        if (lastLanguageName !== null) {
            const lastContainer = document.createElement('div');
            lastContainer.innerHTML = `</div></div>`;
            recommendedlanguagesSection.appendChild(lastContainer);
        }

        // Create a new language section with a new scrollable container
        const languageSection = document.createElement('div');
        languageSection.classList.add('language-section');
        languageSection.innerHTML = `<h3>${language_name}</h3><div class='scrollable-container'>`;
        recommendedlanguagesSection.appendChild(languageSection);

        lastLanguageName = language_name; // Update last language name
    }
    // Create and append the tile
    const tile = document.createElement('div');
    tile.classList.add('tile');
    tile.innerHTML = `
        <iframe width='100%' src='${embed_link}' title='${language_name}' frameborder='0' allowfullscreen></iframe>
        <a href='${video_link}' target='_blank'>
            <h4 class='clickable'>${video_name}</h4>
        </a>`;
    recommendedlanguagesSection.lastChild.lastChild.appendChild(tile);
}

// Close the last language section after the loop
if (lastLanguageName !== null) {
    const closingDiv = document.createElement('div');
    closingDiv.innerHTML = `</div></div>`;
    recommendedlanguagesSection.appendChild(closingDiv);
}
}
function showLanguageSelection() {
    
    const container=document.getElementById('languageSelectionContainer');
    document.getElementById('intro-section').style.display = "none";
    document.querySelector('header').style.display = 'none';
    document.querySelector('footer').style.display = 'none';

    fetch('./static/languages.html') 
        .then(response => response.text())
        .then(html => {
            container.innerHTML = html;
            container.style.display='block';
            document.body.appendChild(container);
            document.getElementById('languageForm').addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent default form submission
                

                const checkedLanguages = Array.from(document.querySelectorAll('input[name="languages"]:checked'))
                    .map(checkbox => checkbox.value);
                
                loadlistoncountry(checkedLanguages);
                document.body.removeChild(container);
                container.style.display='none';
                document.querySelector('header').style.display = 'block';
                document.querySelector('footer').style.display = 'block';
                startAssessment();
            });
        })
        .catch(error => {
            console.error('Error loading the language selection:', error);
        });
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