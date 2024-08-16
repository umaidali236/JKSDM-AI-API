

document.addEventListener("DOMContentLoaded", function() {
    // Attach event listeners to options
    const options = document.querySelectorAll(".option");
    options.forEach(option => {
        option.addEventListener("click", function() {
            // Remove 'selected' class from all options in the current question
            this.parentNode.querySelectorAll(".option").forEach(opt => opt.classList.remove("selected"));
            
            // Add 'selected' class to the clicked option
            this.classList.add("selected");
        });
    });
});




function startAssessment() {
    document.getElementById("loading").style.display ='block';
    sendAJAXRequest();
}

function nextQuestion(questionNumber) {
    // Hide all question sliders
    const questions = document.querySelectorAll('.question-slider');
    questions.forEach(question => question.style.display = 'none');

    // Show the selected question slider
    const question = document.getElementById('question-' + questionNumber);
    if (question) {
        question.style.display = 'block';
    }
}

function completeAssessment() {
    // Collect selected options
    const teamworkSelection = document.querySelector('#question-1 .selected');
    const entrepreneurshipInterestSelection = document.querySelector('#question-2 .selected');
    const technicalSkillsSelection = document.querySelector('#question-3 .selected');

    console.log(`Teamwork: ${teamworkSelection ? teamworkSelection.textContent : 'Not Selected'}`);
    console.log(`Entrepreneurship Interest: ${entrepreneurshipInterestSelection ? entrepreneurshipInterestSelection.textContent : 'Not Selected'}`);
    console.log(`Technical Skills: ${technicalSkillsSelection ? technicalSkillsSelection.textContent : 'Not Selected'}`);

    // Hide the psychometric section and show the hero section
    document.getElementById("psychometric-section").style.display = "none";
    document.getElementById("hero").style.display = "block";
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => section.style.display = 'none');

    // Show the selected section
    document.getElementById(sectionId).style.display = 'block';
}



var response = {}
function sendAJAXRequest() {
    
    var xhr = new XMLHttpRequest();
    var url = "http://127.0.0.1:5000/api/v1/questionBank";
    
    

    var params = "sectors=" +JSON.stringify(sectorsSelected) + "&numQuestionsInEachSector=2";
    
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
    console.log(responseDict.message);
    responseDict.message.forEach(sectorquestions => {
        console.log(sectorquestions.sector);
    });


    document.getElementById("intro-section").style.display = "none";
    document.getElementById("loading").style.display = "none";
    document.getElementById("psychometric-section").style.display = "block";
   //sectorsSelected.forEach(selectedSector=> {
        //    sectorssection.innerHTML+= "<span id='smallbutton'>"+selectedSector+"</span>";
        // psychometricsection.innerHTML += "<div class='question-slider' id='question-1">
        //     <div class="question">
        //         <p>How comfortable are you with working in teams?</p>
        //     </div>
        //     <div class="option" onclick="selectOption('teamwork', 'option1')">Very Comfortable</div>
        //     <div class="option" onclick="selectOption('teamwork', 'option2')">Somewhat Comfortable</div>
        //     <div class="option" onclick="selectOption('teamwork', 'option3')">Neutral</div>
        //     <div class="option" onclick="selectOption('teamwork', 'option4')">Not Comfortable</div>
            
        //     <button onclick="nextQuestion(2)">Next</button>
        // </div>


    }
        



        
        
     

