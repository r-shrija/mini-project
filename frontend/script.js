async function sendMessage(){

let input=document.getElementById("userInput").value;

if(input==="") return;

let chatbox=document.getElementById("chatbox");

/* show user message */

chatbox.innerHTML +=
"<div class='user'><span>"+input+"</span></div>";

document.getElementById("userInput").value="";

/* send to backend */

let response=await fetch("http://127.0.0.1:5000/chat",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({message:input})

});

let data=await response.json();

/* show bot reply */

chatbox.innerHTML +=
"<div class='bot'><span>"+data.reply+"</span></div>";

chatbox.scrollTop=chatbox.scrollHeight;

}


/* voice recognition */

function startVoice(){

const recognition=new webkitSpeechRecognition();

recognition.onresult=function(event){

document.getElementById("userInput").value =
event.results[0][0].transcript;

}

recognition.start();

}


/* STUDY PLAN */

async function createStudyPlan(){

let examDate=document.getElementById("examDate").value;

let subjects=document.getElementById("subjects").value;

let hours=document.getElementById("hours").value;

let response=await fetch("http://127.0.0.1:5000/study-plan",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
exam_date:examDate,
subjects:subjects,
hours:hours
})

});

let data=await response.json();

let result=document.getElementById("studyResult");

/* show AI result */

result.innerHTML="<h3>Your AI Study Plan</h3>";

result.innerHTML+="<pre>"+data.plan+"</pre>";

}