// ------------------- Chat -------------------
async function sendMessage() {
    let input = document.getElementById("userInput").value;
    if (input === "") return;

    let chatbox = document.getElementById("chatbox");
    chatbox.innerHTML += "<div class='user'><span>" + input + "</span></div>";
    document.getElementById("userInput").value = "";

    try {
        let response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: input})
        });
        let data = await response.json();
        chatbox.innerHTML += "<div class='bot'><span>" + data.reply + "</span></div>";
        chatbox.scrollTop = chatbox.scrollHeight;
    } catch (err) {
        console.error("Chat error:", err);
    }
}

function startVoice() {
    const recognition = new webkitSpeechRecognition();
    recognition.onresult = function(event) {
        document.getElementById("userInput").value = event.results[0][0].transcript;
    }
    recognition.start();
}

// ------------------- Study Plan -------------------
async function createStudyPlan() {
    let examDate = document.getElementById("examDate").value;
    let subjects = document.getElementById("subjects").value;
    let hours = document.getElementById("hours").value;

    try {
        let response = await fetch("http://127.0.0.1:5000/study-plan", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({exam_date: examDate, subjects: subjects, hours: hours})
        });
        let data = await response.json();
        let result = document.getElementById("studyResult");
        result.innerHTML = "<h3>Your AI Study Plan</h3><pre>" + data.plan + "</pre>";
    } catch (err) {
        console.error("Study Plan error:", err);
    }
}

// ------------------- Quiz -------------------
let currentQuestionId = null;
let quizUserId = "user123";

async function startQuiz() {
    document.getElementById("quizBox").style.display = "block";
    try {
        let res = await fetch(`http://127.0.0.1:5000/quiz/start?user_id=${quizUserId}`);
        let data = await res.json();
        displayQuizQuestion(data);
    } catch (err) {
        console.error("Quiz start error:", err);
    }
}

function displayQuizQuestion(data) {
    if (data.message) {
        document.getElementById("quizQuestion").innerText = data.message;
        document.getElementById("quizOptions").innerHTML = "";
        document.getElementById("quizFeedback").innerText = "";
        return;
    }

    currentQuestionId = data.question_id;
    document.getElementById("quizQuestion").innerText = data.question_text;

    let optionsDiv = document.getElementById("quizOptions");
    optionsDiv.innerHTML = "";
    data.options.forEach(opt => {
        let btn = document.createElement("button");
        btn.innerText = opt;
        btn.onclick = () => submitQuizAnswer(opt);
        optionsDiv.appendChild(btn);
    });

    document.getElementById("quizFeedback").innerText = "";
}

async function submitQuizAnswer(answer) {
    try {
        let res = await fetch("http://127.0.0.1:5000/quiz/answer", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({user_id: quizUserId, question_id: currentQuestionId, answer: answer})
        });
        let data = await res.json();
        document.getElementById("quizFeedback").innerText = data.correct !== undefined 
            ? (data.correct ? "Correct ✅" : "Wrong ❌") 
            : "";

        displayQuizQuestion(data);
    } catch (err) {
        console.error("Quiz submit error:", err);
    }
}