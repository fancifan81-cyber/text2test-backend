<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Text2Test AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f5f7fb;
    color: #222;
}

.container {
    max-width: 1100px;
    margin: 40px auto;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 30px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}

h1 {
    text-align: center;
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

.section {
    margin-bottom: 25px;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 8px;
}

input[type="file"],
input[type="text"],
input[type="number"],
textarea,
select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 10px;
    background: white;
    font-size: 15px;
}

textarea {
    min-height: 100px;
    resize: vertical;
}

input[type="range"] {
    width: 100%;
}

.range-value {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    margin-top: 5px;
}

button {
    border: none;
    border-radius: 10px;
    padding: 13px 22px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.generate-btn {
    width: 100%;
    background: #111827;
    color: white;
}

.generate-btn:hover {
    background: #000;
}

.finish-btn {
    width: 100%;
    background: #16a34a;
    color: white;
    margin-top: 20px;
}

.finish-btn:hover {
    background: #15803d;
}

.save-exam-btn {
    width: 100%;
    background: #7c3aed;
    color: white;
    margin-top: 20px;
}

.save-exam-btn:hover {
    background: #6d28d9;
}

.new-test-btn {
    width: 100%;
    background: #2563eb;
    color: white;
    margin-top: 15px;
}

.new-test-btn:hover {
    background: #1d4ed8;
}

.library-btn {
    width: 100%;
    background: #0f766e;
    color: white;
    margin-top: 15px;
}

.library-btn:hover {
    background: #115e59;
}

.status {
    margin-top: 20px;
    padding: 15px;
    border-radius: 10px;
    display: none;
}

.loading {
    background: #eff6ff;
    color: #1d4ed8;
}

.error {
    background: #fef2f2;
    color: #dc2626;
}

.success {
    background: #f0fdf4;
    color: #15803d;
}

#testArea {
    display: none;
    margin-top: 30px;
}

.question {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 20px;
}

.question-title {
    font-size: 17px;
    font-weight: bold;
    margin-bottom: 15px;
}

.option {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    cursor: pointer;
    background: white;
}

.option:hover {
    background: #f3f4f6;
}

.option input {
    margin-top: 3px;
}

.option.correct {
    border: 2px solid #16a34a;
    background: #f0fdf4;
}

.option.wrong {
    border: 2px solid #dc2626;
    background: #fef2f2;
}

.answer-box {
    margin-top: 12px;
    padding: 10px;
    border-radius: 8px;
    display: none;
    font-weight: bold;
}

.correct-answer {
    color: #15803d;
    background: #f0fdf4;
}

.wrong-answer {
    color: #dc2626;
    background: #fef2f2;
}

.short-answer-input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 15px;
}

.result {
    display: none;
    text-align: center;
    background: #f8fafc;
    border-radius: 15px;
    padding: 25px;
    margin-top: 20px;
}

.score {
    font-size: 42px;
    font-weight: bold;
    margin: 10px 0;
}

.result-text {
    color: #555;
}

.file-name {
    margin-top: 8px;
    color: #666;
    font-size: 14px;
}

#saveExamSection {
    display: none;
    margin-top: 30px;
    padding-top: 30px;
    border-top: 2px solid #e5e7eb;
}

.save-title {
    margin-bottom: 8px;
}

.save-subtitle {
    color: #666;
    margin-bottom: 25px;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

.full-width {
    grid-column: 1 / -1;
}

.progress-section {
    margin-top: 35px;
    padding-top: 30px;
    border-top: 1px solid #e5e7eb;
}

.progress-title {
    font-size: 25px;
    margin-bottom: 8px;
}

.progress-subtitle {
    color: #666;
    margin-bottom: 20px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}

.stat-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}

.stat-number {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 5px;
}

.stat-label {
    color: #666;
    font-size: 14px;
}

.weak-area {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 25px;
}

.weak-area h3 {
    margin-top: 0;
}

.topic-row {
    margin-bottom: 18px;
}

.topic-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 7px;
    font-size: 14px;
    font-weight: bold;
}

.progress-bar {
    width: 100%;
    height: 10px;
    background: #e5e7eb;
    border-radius: 20px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #2563eb;
    border-radius: 20px;
}

.history-title {
    margin-top: 30px;
    margin-bottom: 15px;
}

.history-item {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
    background: white;
}

.history-top {
    display: flex;
    justify-content: space-between;
    gap: 15px;
}

.history-file {
    font-weight: bold;
    word-break: break-word;
}

.history-score {
    font-weight: bold;
    white-space: nowrap;
}

.history-meta {
    color: #666;
    font-size: 13px;
    margin-top: 6px;
}

.clear-history-btn {
    background: #f3f4f6;
    color: #374151;
    font-size: 13px;
    padding: 9px 14px;
    margin-top: 10px;
}

.clear-history-btn:hover {
    background: #e5e7eb;
}

.no-history {
    color: #777;
    text-align: center;
    padding: 20px;
    background: #f8fafc;
    border-radius: 12px;
}


/* ==================================================
   TEST LIBRARY
================================================== */

.library-section {
    margin-top: 40px;
    padding-top: 30px;
    border-top: 2px solid #e5e7eb;
}

.library-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    margin-bottom: 10px;
}

.library-title {
    margin: 0;
    font-size: 28px;
}

.library-subtitle {
    color: #666;
    margin-bottom: 25px;
}

.library-filters {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 12px;
    margin-bottom: 25px;
}

.search-input {
    width: 100%;
}

.refresh-btn {
    background: #f3f4f6;
    color: #374151;
    white-space: nowrap;
}

.refresh-btn:hover {
    background: #e5e7eb;
}

.library-status {
    display: none;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.library-loading {
    background: #eff6ff;
    color: #1d4ed8;
}

.library-error {
    background: #fef2f2;
    color: #dc2626;
}

.exam-list {
    display: grid;
    gap: 15px;
}

.exam-card {
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 20px;
    background: white;
    transition: 0.2s;
}

.exam-card:hover {
    box-shadow: 0 5px 18px rgba(0,0,0,0.07);
    transform: translateY(-1px);
}

.exam-card-title {
    font-size: 19px;
    font-weight: bold;
    margin-bottom: 10px;
}

.exam-card-description {
    color: #666;
    font-size: 14px;
    margin-bottom: 15px;
}

.exam-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
}

.exam-tag {
    background: #f3f4f6;
    color: #374151;
    border-radius: 20px;
    padding: 6px 10px;
    font-size: 12px;
}

.exam-card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
}

.open-exam-btn {
    background: #2563eb;
    color: white;
    padding: 10px 18px;
}

.open-exam-btn:hover {
    background: #1d4ed8;
}

.exam-date {
    color: #777;
    font-size: 13px;
}

.library-empty {
    text-align: center;
    padding: 35px 20px;
    background: #f8fafc;
    border-radius: 14px;
    color: #777;
}

#libraryTestArea {
    display: none;
    margin-top: 30px;
    padding-top: 30px;
    border-top: 2px solid #e5e7eb;
}

.library-test-title {
    font-size: 26px;
    margin-bottom: 8px;
}

.library-test-meta {
    color: #666;
    margin-bottom: 25px;
}

.reuse-btn {
    width: 100%;
    background: #7c3aed;
    color: white;
    margin-top: 20px;
}

.reuse-btn:hover {
    background: #6d28d9;
}

.close-library-test-btn {
    width: 100%;
    background: #f3f4f6;
    color: #374151;
    margin-top: 10px;
}


/* ==================================================
   RESPONSIVE
================================================== */

@media (max-width: 750px) {

    .library-filters {
        grid-template-columns: 1fr;
    }

    .library-header {
        flex-direction: column;
        align-items: flex-start;
    }

}

@media (max-width: 600px) {

    .container {
        margin: 10px auto;
        padding: 10px;
    }

    .card {
        padding: 20px;
    }

    h1 {
        font-size: 26px;
    }

    .stats-grid,
    .form-grid {
        grid-template-columns: 1fr;
    }

    .full-width {
        grid-column: auto;
    }

    .history-top {
        flex-direction: column;
        gap: 5px;
    }

    .exam-card-footer {
        flex-direction: column;
        align-items: stretch;
    }

    .open-exam-btn {
        width: 100%;
    }

}

</style>

</head>


<body>


<div class="container">

<div class="card">


<h1>📚 Text2Test AI</h1>

<div class="subtitle">
Turn your textbook PDF into a personalized test with AI
</div>


<!-- ==================================================
     GENERATE TEST
================================================== -->

<div class="section">

<label>1. Upload your textbook PDF</label>

<input
    type="file"
    id="pdfFile"
    accept=".pdf,application/pdf"
>

<div id="fileName" class="file-name"></div>

</div>


<div class="section">

<label>2. Number of questions</label>

<input
    type="range"
    id="questionCount"
    min="10"
    max="40"
    value="20"
>

<div id="questionCountValue" class="range-value">
20
</div>

</div>


<div class="section">

<label>3. Difficulty</label>

<select id="difficulty">

<option value="easy">
Easy
</option>

<option value="medium" selected>
Medium
</option>

<option value="hard">
Hard
</option>

</select>

</div>


<div class="section">

<label>4. Question type</label>

<select id="questionType">

<option value="multiple_choice" selected>
Multiple Choice
</option>

<option value="true_false">
True / False
</option>

<option value="short_answer">
Short Answer
</option>

</select>

</div>


<button
    type="button"
    id="generateBtn"
    class="generate-btn">

Generate Test

</button>


<div id="status" class="status"></div>


<!-- ==================================================
     GENERATED TEST
================================================== -->

<div id="testArea">

<h2>Your Test</h2>

<div id="questionsContainer"></div>


<button
    type="button"
    id="finishBtn"
    class="finish-btn">

Finish Test

</button>


<div id="result" class="result">

<h2>🎉 Test Completed</h2>

<div id="score" class="score"></div>

<div id="resultText" class="result-text"></div>

</div>


<!-- ==================================================
     SAVE EXAM
================================================== -->

<div id="saveExamSection">

<h2 class="save-title">
💾 Save this exam
</h2>

<div class="save-subtitle">
Classify your generated test before saving it to the shared question bank.
</div>


<div class="form-grid">


<div class="full-width">

<label>Exam title *</label>

<input
    type="text"
    id="examTitle"
    placeholder="Example: Biology Chapter 1 Practice Test"
>

</div>


<div>

<label>Subject *</label>

<select id="subjectId">

<option value="">
Select a subject
</option>

</select>

</div>


<div>

<label>Grade</label>

<select id="grade">

<option value="">
Select grade
</option>

<option value="6">Grade 6</option>
<option value="7">Grade 7</option>
<option value="8">Grade 8</option>
<option value="9">Grade 9</option>
<option value="10">Grade 10</option>
<option value="11">Grade 11</option>
<option value="12">Grade 12</option>

</select>

</div>


<div>

<label>Topic</label>

<input
    type="text"
    id="topic"
    placeholder="Example: Cell Biology"
>

</div>


<div>

<label>Exam type</label>

<select id="examType">

<option value="">
Select exam type
</option>

<option value="Practice">
Practice
</option>

<option value="Quiz">
Quiz
</option>

<option value="Midterm">
Midterm
</option>

<option value="Final">
Final
</option>

<option value="Revision">
Revision
</option>

</select>

</div>


<div>

<label>Year</label>

<input
    type="number"
    id="examYear"
    placeholder="2026"
    min="2000"
    max="2100"
>

</div>


<div class="full-width">

<label>Description</label>

<textarea
    id="description"
    placeholder="Optional description about this exam..."
></textarea>

</div>

</div>


<button
    type="button"
    id="saveExamBtn"
    class="save-exam-btn">

💾 Save Exam

</button>

</div>


<button
    type="button"
    id="newTestBtn"
    class="new-test-btn">

Generate Another Test

</button>

</div>


<!-- ==================================================
     TEST LIBRARY
================================================== -->

<div class="library-section">

<div class="library-header">

<h2 class="library-title">
📚 Test Library
</h2>

</div>

<div class="library-subtitle">
Browse and reuse tests saved in the shared question bank.
</div>


<div class="library-filters">


<input
    type="text"
    id="librarySearch"
    class="search-input"
    placeholder="Search by title, topic, or description..."
>


<select id="librarySubject">

<option value="">
All Subjects
</option>

</select>


<select id="libraryGrade">

<option value="">
All Grades
</option>

<option value="6">Grade 6</option>
<option value="7">Grade 7</option>
<option value="8">Grade 8</option>
<option value="9">Grade 9</option>
<option value="10">Grade 10</option>
<option value="11">Grade 11</option>
<option value="12">Grade 12</option>

</select>


<button
    type="button"
    id="refreshLibraryBtn"
    class="refresh-btn">

↻ Refresh

</button>

</div>


<div
    id="libraryStatus"
    class="library-status">
</div>


<div
    id="examList"
    class="exam-list">

<div class="library-empty">
Loading saved tests...
</div>

</div>


<!-- ==================================================
     LIBRARY TEST VIEW
================================================== -->

<div id="libraryTestArea">

<h2
    id="libraryTestTitle"
    class="library-test-title">
Test
</h2>

<div
    id="libraryTestMeta"
    class="library-test-meta">
</div>

<div id="libraryQuestionsContainer"></div>


<button
    type="button"
    id="libraryFinishBtn"
    class="finish-btn">

Finish Test

</button>


<div
    id="libraryResult"
    class="result">

<h2>🎉 Test Completed</h2>

<div
    id="libraryScore"
    class="score">
</div>

<div
    id="libraryResultText"
    class="result-text">
</div>

</div>


<button
    type="button"
    id="reuseBtn"
    class="reuse-btn">

🔄 Reuse This Test

</button>


<button
    type="button"
    id="closeLibraryTestBtn"
    class="close-library-test-btn">

Close Test

</button>

</div>

</div>


<!-- ==================================================
     MY PROGRESS
================================================== -->

<div class="progress-section">

<h2 class="progress-title">
📊 My Progress
</h2>

<div class="progress-subtitle">
Track your performance and discover where you need more practice.
</div>


<div class="stats-grid">


<div class="stat-card">

<div id="totalTests" class="stat-number">
0
</div>

<div class="stat-label">
Tests Completed
</div>

</div>


<div class="stat-card">

<div id="averageScore" class="stat-number">
0%
</div>

<div class="stat-label">
Average Score
</div>

</div>


<div class="stat-card">

<div id="totalQuestions" class="stat-number">
0
</div>

<div class="stat-label">
Questions Answered
</div>

</div>


</div>


<div id="weakArea" class="weak-area">

<h3>🎯 Areas to Improve</h3>

<div id="weakAreaText">
Complete a test to discover your weakest areas.
</div>

</div>


<h3>📈 Performance by Topic</h3>

<div id="topicStats">

<div class="no-history">
Complete a test to see your topic performance.
</div>

</div>


<h3 class="history-title">
📜 Test History
</h3>


<div id="historyContainer">

<div class="no-history">
No tests completed yet.
</div>

</div>


<button
    type="button"
    id="clearHistoryBtn"
    class="clear-history-btn">

Clear History

</button>

</div>


</div>

</div>


<script>


/* ==================================================
   BACKEND
================================================== */

const BACKEND_URL =
    "https://text2test-backend.onrender.com";

const GENERATE_URL =
    BACKEND_URL + "/upload-pdf";

const SAVE_EXAM_URL =
    BACKEND_URL + "/save-exam";

const SUBJECTS_URL =
    BACKEND_URL + "/subjects";

const EXAMS_URL =
    BACKEND_URL + "/exams";


/* ==================================================
   ELEMENTS
================================================== */

const pdfFile =
    document.getElementById("pdfFile");

const fileName =
    document.getElementById("fileName");

const questionCount =
    document.getElementById("questionCount");

const questionCountValue =
    document.getElementById("questionCountValue");

const difficulty =
    document.getElementById("difficulty");

const questionType =
    document.getElementById("questionType");

const generateBtn =
    document.getElementById("generateBtn");

const status =
    document.getElementById("status");

const testArea =
    document.getElementById("testArea");

const questionsContainer =
    document.getElementById("questionsContainer");

const finishBtn =
    document.getElementById("finishBtn");

const result =
    document.getElementById("result");

const score =
    document.getElementById("score");

const resultText =
    document.getElementById("resultText");

const newTestBtn =
    document.getElementById("newTestBtn");

const saveExamSection =
    document.getElementById("saveExamSection");

const saveExamBtn =
    document.getElementById("saveExamBtn");

const examTitle =
    document.getElementById("examTitle");

const subjectId =
    document.getElementById("subjectId");

const grade =
    document.getElementById("grade");

const topic =
    document.getElementById("topic");

const examType =
    document.getElementById("examType");

const examYear =
    document.getElementById("examYear");

const description =
    document.getElementById("description");

const totalTests =
    document.getElementById("totalTests");

const averageScore =
    document.getElementById("averageScore");

const totalQuestions =
    document.getElementById("totalQuestions");

const weakAreaText =
    document.getElementById("weakAreaText");

const topicStats =
    document.getElementById("topicStats");

const historyContainer =
    document.getElementById("historyContainer");

const clearHistoryBtn =
    document.getElementById("clearHistoryBtn");


/* ==================================================
   LIBRARY ELEMENTS
================================================== */

const librarySearch =
    document.getElementById("librarySearch");

const librarySubject =
    document.getElementById("librarySubject");

const libraryGrade =
    document.getElementById("libraryGrade");

const refreshLibraryBtn =
    document.getElementById("refreshLibraryBtn");

const libraryStatus =
    document.getElementById("libraryStatus");

const examList =
    document.getElementById("examList");

const libraryTestArea =
    document.getElementById("libraryTestArea");

const libraryTestTitle =
    document.getElementById("libraryTestTitle");

const libraryTestMeta =
    document.getElementById("libraryTestMeta");

const libraryQuestionsContainer =
    document.getElementById("libraryQuestionsContainer");

const libraryFinishBtn =
    document.getElementById("libraryFinishBtn");

const libraryResult =
    document.getElementById("libraryResult");

const libraryScore =
    document.getElementById("libraryScore");

const libraryResultText =
    document.getElementById("libraryResultText");

const reuseBtn =
    document.getElementById("reuseBtn");

const closeLibraryTestBtn =
    document.getElementById("closeLibraryTestBtn");


/* ==================================================
   STATE
================================================== */

let questions = [];

let testFinished = false;

let libraryQuestions = [];

let libraryTestFinished = false;

let currentLibraryExam = null;

let currentTestInfo = {

    filename: "",

    difficulty: "",

    questionType: "",

    questionCount: 0

};


/* ==================================================
   HISTORY
================================================== */

const HISTORY_KEY =
    "text2test_history";


/* ==================================================
   QUESTION COUNT
================================================== */

questionCount.addEventListener(
    "input",
    function() {

        questionCountValue.textContent =
            questionCount.value;

    }
);


/* ==================================================
   FILE
================================================== */

pdfFile.addEventListener(
    "change",
    function() {

        if (
            pdfFile.files &&
            pdfFile.files.length > 0
        ) {

            fileName.textContent =
                "Selected: " +
                pdfFile.files[0].name;

        } else {

            fileName.textContent = "";

        }

    }
);


/* ==================================================
   STATUS
================================================== */

function showStatus(message, type) {

    status.textContent = message;

    status.className =
        "status " + type;

    status.style.display =
        "block";

}


/* ==================================================
   LIBRARY STATUS
================================================== */

function showLibraryStatus(
    message,
    type
) {

    libraryStatus.textContent =
        message;

    libraryStatus.className =
        "library-status " + type;

    libraryStatus.style.display =
        "block";

}


function hideLibraryStatus() {

    libraryStatus.style.display =
        "none";

}


/* ==================================================
   HISTORY
================================================== */

function getHistory() {

    try {

        const saved =
            localStorage.getItem(
                HISTORY_KEY
            );

        if (!saved) {
            return [];
        }

        const parsed =
            JSON.parse(saved);

        return Array.isArray(parsed)
            ? parsed
            : [];

    } catch (error) {

        console.error(
            "History error:",
            error
        );

        return [];

    }

}


function saveHistory(testData) {

    try {

        const history =
            getHistory();

        history.unshift(testData);

        localStorage.setItem(
            HISTORY_KEY,
            JSON.stringify(
                history.slice(0, 50)
            )
        );

    } catch (error) {

        console.error(
            "Could not save history:",
            error
        );

    }

    updateProgress();

}


/* ==================================================
   ESCAPE HTML
================================================== */

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;

}


/* ==================================================
   CAPITALIZE
================================================== */

function capitalize(value) {

    if (!value) {
        return "";
    }

    return value.charAt(0).toUpperCase()
        + value.slice(1);

}


/* ==================================================
   QUESTION TYPE
================================================== */

function formatQuestionType(type) {

    if (
        type ===
        "multiple_choice"
    ) {
        return "Multiple Choice";
    }

    if (
        type ===
        "true_false"
    ) {
        return "True / False";
    }

    if (
        type ===
        "short_answer"
    ) {
        return "Short Answer";
    }

    return type || "";

}


/* ==================================================
   LOAD SUBJECTS
================================================== */

async function loadSubjects() {

    try {

        const response =
            await fetch(
                SUBJECTS_URL
            );

        const data =
            await response.json();

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                data.message ||
                "Could not load subjects."
            );

        }


        subjectId.innerHTML =
            '<option value="">Select a subject</option>';

        librarySubject.innerHTML =
            '<option value="">All Subjects</option>';


        data.subjects.forEach(
            function(subject) {

                const id =
                    subject.id;

                const name =
                    subject.Name ||
                    subject.name ||
                    "Unknown Subject";


                const saveOption =
                    document.createElement(
                        "option"
                    );

                saveOption.value =
                    id;

                saveOption.textContent =
                    name;

                subjectId.appendChild(
                    saveOption
                );


                const libraryOption =
                    document.createElement(
                        "option"
                    );

                libraryOption.value =
                    id;

                libraryOption.textContent =
                    name;

                librarySubject.appendChild(
                    libraryOption
                );

            }
        );


    } catch (error) {

        console.error(
            "Subject loading error:",
            error
        );

        subjectId.innerHTML =
            '<option value="">Could not load subjects</option>';

        librarySubject.innerHTML =
            '<option value="">Could not load subjects</option>';

    }

}


/* ==================================================
   LOAD TEST LIBRARY
================================================== */

async function loadLibrary() {

    hideLibraryStatus();

    examList.innerHTML =
        '<div class="library-empty">Loading saved tests...</div>';


    const params =
        new URLSearchParams();


    if (librarySubject.value) {

        params.set(
            "subject_id",
            librarySubject.value
        );

    }


    if (libraryGrade.value) {

        params.set(
            "grade",
            libraryGrade.value
        );

    }


    if (librarySearch.value.trim()) {

        params.set(
            "search",
            librarySearch.value.trim()
        );

    }


    const url =
        EXAMS_URL +
        (
            params.toString()
                ? "?" + params.toString()
                : ""
        );


    try {

        const response =
            await fetch(url);


        const rawText =
            await response.text();


        let data;


        try {

            data =
                JSON.parse(rawText);

        } catch (error) {

            throw new Error(
                "Backend returned invalid JSON."
            );

        }


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                data.message ||
                "Could not load Test Library."
            );

        }


        renderExamList(
            data.exams || []
        );


    } catch (error) {

        console.error(
            "Library error:",
            error
        );


        examList.innerHTML =
            '<div class="library-empty">' +
            'Could not load the Test Library.' +
            '</div>';


        showLibraryStatus(
            "❌ " + error.message,
            "library-error"
        );

    }

}


/* ==================================================
   RENDER EXAM LIST
================================================== */

function renderExamList(exams) {

    examList.innerHTML = "";


    if (!exams.length) {

        examList.innerHTML =
            '<div class="library-empty">' +
            'No saved tests found.' +
            '</div>';

        return;

    }


    exams.forEach(
        function(exam) {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "exam-card";


            const subject =
                exam.subjects &&
                (
                    exam.subjects.Name ||
                    exam.subjects.name
                )
                    ? (
                        exam.subjects.Name ||
                        exam.subjects.name
                    )
                    : "Unknown Subject";


            const title =
                escapeHTML(
                    exam.title ||
                    "Untitled Test"
                );


            const examDescription =
                exam.description
                    ? escapeHTML(
                        exam.description
                    )
                    : "No description provided.";


            const gradeText =
                exam.grade
                    ? "Grade " +
                      escapeHTML(
                          exam.grade
                      )
                    : "Grade not specified";


            const topicText =
                exam.topic
                    ? escapeHTML(
                        exam.topic
                    )
                    : "General";


            const typeText =
                exam.exam_type
                    ? escapeHTML(
                        exam.exam_type
                    )
                    : "Practice";


            let dateText = "";


            if (exam.created_at) {

                const date =
                    new Date(
                        exam.created_at
                    );

                if (
                    !isNaN(
                        date.getTime()
                    )
                ) {

                    dateText =
                        date.toLocaleDateString(
                            "en-US",
                            {
                                year: "numeric",
                                month: "short",
                                day: "numeric"
                            }
                        );

                }

            }


            card.innerHTML =

                '<div class="exam-card-title">' +
                    '📄 ' +
                    title +
                '</div>' +

                '<div class="exam-card-description">' +
                    examDescription +
                '</div>' +

                '<div class="exam-meta">' +

                    '<span class="exam-tag">' +
                        escapeHTML(
                            subject
                        ) +
                    '</span>' +

                    '<span class="exam-tag">' +
                        gradeText +
                    '</span>' +

                    '<span class="exam-tag">' +
                        topicText +
                    '</span>' +

                    '<span class="exam-tag">' +
                        typeText +
                    '</span>' +

                '</div>' +

                '<div class="exam-card-footer">' +

                    '<div class="exam-date">' +
                        (
                            dateText
                                ? "Saved " +
                                  dateText
                                : ""
                        ) +
                    '</div>' +

                    '<button ' +
                        'type="button" ' +
                        'class="open-exam-btn">' +
                        'Open Test' +
                    '</button>' +

                '</div>';


            const openButton =
                card.querySelector(
                    ".open-exam-btn"
                );


            openButton.addEventListener(
                "click",
                function() {

                    openLibraryExam(
                        exam.id
                    );

                }
            );


            examList.appendChild(
                card
            );

        }
    );

}


/* ==================================================
   OPEN SAVED EXAM
================================================== */

async function openLibraryExam(
    examId
) {

    showLibraryStatus(
        "Loading test...",
        "library-loading"
    );


    try {

        const response =
            await fetch(
                BACKEND_URL +
                "/exams/" +
                encodeURIComponent(
                    examId
                )
            );


        const rawText =
            await response.text();


        let data;


        try {

            data =
                JSON.parse(rawText);

        } catch (error) {

            throw new Error(
                "Backend returned invalid JSON."
            );

        }


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.error ||
                data.message ||
                "Could not open this test."
            );

        }


        currentLibraryExam =
            data.exam;


        libraryQuestions =
            Array.isArray(
                data.questions
            )
                ? data.questions
                : [];


        if (
            !libraryQuestions.length
        ) {

            throw new Error(
                "This test does not contain any questions."
            );

        }


        renderLibraryTest();


        hideLibraryStatus();


        libraryTestArea.style.display =
            "block";


        libraryTestArea.scrollIntoView({
            behavior: "smooth"
        });


    } catch (error) {

        console.error(
            "Open exam error:",
            error
        );


        showLibraryStatus(
            "❌ " + error.message,
            "library-error"
        );

    }

}


/* ==================================================
   RENDER LIBRARY TEST
================================================== */

function renderLibraryTest() {

    libraryQuestionsContainer.innerHTML =
        "";

    libraryResult.style.display =
        "none";

    libraryFinishBtn.disabled =
        false;

    libraryTestFinished =
        false;


    const exam =
        currentLibraryExam || {};


    libraryTestTitle.textContent =
        exam.title ||
        "Saved Test";


    const subject =
        exam.subjects &&
        (
            exam.subjects.Name ||
            exam.subjects.name
        )
            ? (
                exam.subjects.Name ||
                exam.subjects.name
            )
            : "Unknown Subject";


    libraryTestMeta.textContent =
        subject +
        (
            exam.grade
                ? " · Grade " +
                  exam.grade
                : ""
        ) +
        (
            exam.topic
                ? " · " +
                  exam.topic
                : ""
        );


    libraryQuestions.forEach(
        function(q, index) {

            const questionDiv =
                document.createElement(
                    "div"
                );

            questionDiv.className =
                "question";


            const title =
                document.createElement(
                    "div"
                );

            title.className =
                "question-title";


            title.textContent =
                "Question " +
                (index + 1) +
                ": " +
                String(
                    q.question || ""
                );


            questionDiv.appendChild(
                title
            );


            let options =
                q.options;


            if (
                typeof options ===
                "string"
            ) {

                try {

                    options =
                        JSON.parse(
                            options
                        );

                } catch (error) {

                    options = {};

                }

            }


            if (
                !options ||
                typeof options !==
                "object"
            ) {

                options = {};

            }


            if (
                Object.keys(options).length
                > 0
            ) {

                Object.keys(options).forEach(
                    function(letter) {

                        const option =
                            document.createElement(
                                "label"
                            );

                        option.className =
                            "option";


                        const input =
                            document.createElement(
                                "input"
                            );

                        input.type =
                            "radio";

                        input.name =
                            "library_question_" +
                            index;

                        input.value =
                            letter;


                        const text =
                            document.createElement(
                                "span"
                            );

                        text.textContent =
                            letter +
                            ". " +
                            String(
                                options[letter] ??
                                ""
                            );


                        option.appendChild(
                            input
                        );

                        option.appendChild(
                            text
                        );


                        questionDiv.appendChild(
                            option
                        );

                    }
                );

            } else {

                const input =
                    document.createElement(
                        "input"
                    );

                input.type =
                    "text";

                input.className =
                    "short-answer-input";

                input.id =
                    "library_short_" +
                    index;

                input.placeholder =
                    "Type your answer here...";


                questionDiv.appendChild(
                    input
                );

            }


            const answerBox =
                document.createElement(
                    "div"
                );

            answerBox.className =
                "answer-box";

            answerBox.id =
                "library_answer_" +
                index;


            questionDiv.appendChild(
                answerBox
            );


            libraryQuestionsContainer
                .appendChild(
                    questionDiv
                );

        }
    );

}


/* ==================================================
   FINISH LIBRARY TEST
================================================== */

libraryFinishBtn.addEventListener(
    "click",
    function() {

        if (libraryTestFinished) {
            return;
        }


        if (!libraryQuestions.length) {
            return;
        }


        let correct = 0;

        let answered = 0;


        libraryQuestions.forEach(
            function(q, index) {

                const questionDiv =
                    libraryQuestionsContainer
                        .children[index];


                const answerBox =
                    document.getElementById(
                        "library_answer_" +
                        index
                    );


                let options =
                    q.options;


                if (
                    typeof options ===
                    "string"
                ) {

                    try {

                        options =
                            JSON.parse(
                                options
                            );

                    } catch (error) {

                        options = {};

                    }

                }


                if (
                    !options ||
                    typeof options !==
                    "object"
                ) {

                    options = {};

                }


                const correctAnswer =
                    String(
                        q.answer || ""
                    )
                    .trim()
                    .toUpperCase();


                let selectedAnswer =
                    null;


                if (
                    Object.keys(options)
                        .length > 0
                ) {

                    const selected =
                        document.querySelector(
                            'input[name="library_question_' +
                            index +
                            '"]:checked'
                        );


                    if (selected) {

                        answered++;

                        selectedAnswer =
                            selected.value
                                .toUpperCase();

                    }


                    const optionElements =
                        questionDiv
                            .querySelectorAll(
                                ".option"
                            );


                    optionElements.forEach(
                        function(option) {

                            const input =
                                option.querySelector(
                                    "input"
                                );


                            input.disabled =
                                true;


                            if (
                                input.value
                                    .toUpperCase() ===
                                correctAnswer
                            ) {

                                option.classList.add(
                                    "correct"
                                );

                            }


                            if (
                                selectedAnswer &&
                                input.value
                                    .toUpperCase() ===
                                selectedAnswer &&
                                selectedAnswer !==
                                correctAnswer
                            ) {

                                option.classList.add(
                                    "wrong"
                                );

                            }

                        }
                    );


                    if (
                        selectedAnswer ===
                        correctAnswer
                    ) {

                        correct++;

                        answerBox.textContent =
                            "✅ Correct! Answer: " +
                            correctAnswer;

                        answerBox.className =
                            "answer-box correct-answer";

                    } else {

                        answerBox.textContent =
                            selectedAnswer
                                ? "❌ Incorrect. Correct answer: " +
                                  correctAnswer
                                : "⚪ Not answered. Correct answer: " +
                                  correctAnswer;

                        answerBox.className =
                            "answer-box wrong-answer";

                    }


                    answerBox.style.display =
                        "block";

                } else {

                    const input =
                        document.getElementById(
                            "library_short_" +
                            index
                        );


                    const userText =
                        input.value.trim();


                    if (userText) {
                        answered++;
                    }


                    input.disabled =
                        true;


                    const correctText =
                        String(
                            q.answer || ""
                        ).trim();


                    const userLower =
                        userText.toLowerCase();


                    const correctLower =
                        correctText.toLowerCase();


                    const isCorrect =
                        userText.length > 0 &&
                        (
                            userLower ===
                            correctLower ||

                            userLower.includes(
                                correctLower
                            ) ||

                            correctLower.includes(
                                userLower
                            )
                        );


                    if (isCorrect) {

                        correct++;

                        answerBox.textContent =
                            "✅ Correct! Answer: " +
                            correctText;

                        answerBox.className =
                            "answer-box correct-answer";

                    } else {

                        answerBox.textContent =
                            "❌ Incorrect. Correct answer: " +
                            correctText;

                        answerBox.className =
                            "answer-box wrong-answer";

                    }


                    answerBox.style.display =
                        "block";

                }

            }
        );


        const total =
            libraryQuestions.length;


        const percentage =
            Math.round(
                correct /
                total *
                100
            );


        libraryScore.textContent =
            correct +
            " / " +
            total;


        libraryResultText.textContent =
            "You answered " +
            answered +
            " out of " +
            total +
            " questions. Score: " +
            percentage +
            "%";


        libraryResult.style.display =
            "block";


        libraryTestFinished =
            true;


        libraryFinishBtn.disabled =
            true;


        saveHistory({

            id:
                Date.now(),

            date:
                new Date().toISOString(),

            filename:
                currentLibraryExam &&
                currentLibraryExam.title
                    ? currentLibraryExam.title
                    : "Saved Test",

            difficulty:
                "medium",

            questionType:
                "multiple_choice",

            total:
                total,

            correct:
                correct,

            percentage:
                percentage,

            questions:
                libraryQuestions.map(
                    function(q, index) {

                        return {

                            topic:
                                q.topic ||
                                currentLibraryExam.topic ||
                                "General",

                            correct:
                                false,

                            correctAnswer:
                                String(
                                    q.answer || ""
                                )

                        };

                    }
                )

        });

    }
);


/* ==================================================
   REUSE SAVED TEST
================================================== */

reuseBtn.addEventListener(
    "click",
    function() {

        if (!currentLibraryExam) {
            return;
        }


        questions =
            libraryQuestions.map(
                function(q) {

                    return {

                        question:
                            q.question,

                        options:
                            q.options || {},

                        answer:
                            q.answer,

                        difficulty:
                            q.difficulty ||
                            "medium",

                        question_type:
                            q.question_type ||
                            "multiple_choice",

                        topic:
                            currentLibraryExam.topic ||
                            "General"

                    };

                }
            );


        currentTestInfo = {

            filename:
                currentLibraryExam.title ||
                "Saved Test",

            difficulty:
                questions[0] &&
                questions[0].difficulty
                    ? questions[0].difficulty
                    : "medium",

            questionType:
                questions[0] &&
                questions[0].question_type
                    ? questions[0].question_type
                    : "multiple_choice",

            questionCount:
                questions.length

        };


        renderQuestions();


        testArea.style.display =
            "block";


        libraryTestArea.style.display =
            "none";


        result.style.display =
            "none";


        saveExamSection.style.display =
            "none";


        showStatus(
            "✅ Test loaded. You can take it again.",
            "success"
        );


        testArea.scrollIntoView({
            behavior: "smooth"
        });

    }
);


/* ==================================================
   CLOSE LIBRARY TEST
================================================== */

closeLibraryTestBtn.addEventListener(
    "click",
    function() {

        libraryTestArea.style.display =
            "none";


        libraryQuestions = [];

        currentLibraryExam = null;


        window.scrollTo({

            top:
                document.querySelector(
                    ".library-section"
                ).offsetTop - 20,

            behavior:
                "smooth"

        });

    }
);


/* ==================================================
   LIBRARY FILTERS
================================================== */

librarySubject.addEventListener(
    "change",
    loadLibrary
);

libraryGrade.addEventListener(
    "change",
    loadLibrary
);

librarySearch.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key ===
            "Enter"
        ) {

            loadLibrary();

        }

    }
);


refreshLibraryBtn.addEventListener(
    "click",
    loadLibrary
);


/* ==================================================
   GENERATE TEST
================================================== */

generateBtn.addEventListener(
    "click",
    async function(event) {

        event.preventDefault();


        if (
            !pdfFile.files ||
            pdfFile.files.length === 0
        ) {

            showStatus(
                "Please upload a PDF first.",
                "error"
            );

            return;

        }


        const file =
            pdfFile.files[0];


        if (
            !file.name
                .toLowerCase()
                .endsWith(".pdf")
        ) {

            showStatus(
                "Please upload a PDF file.",
                "error"
            );

            return;

        }


        generateBtn.disabled =
            true;

        generateBtn.textContent =
            "Generating Test...";


        showStatus(
            "🤖 AI is reading your textbook and creating your test. Please wait...",
            "loading"
        );


        testArea.style.display =
            "none";

        result.style.display =
            "none";

        saveExamSection.style.display =
            "none";


        const formData =
            new FormData();


        formData.append(
            "pdf",
            file
        );


        formData.append(
            "question_count",
            String(
                questionCount.value
            )
        );


        formData.append(
            "difficulty",
            difficulty.value
        );


        formData.append(
            "question_type",
            questionType.value
        );


        try {

            const response =
                await fetch(
                    GENERATE_URL,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const rawText =
                await response.text();


            let data;


            try {

                data =
                    JSON.parse(
                        rawText
                    );

            } catch (error) {

                throw new Error(
                    "The server returned an invalid response."
                );

            }


            if (!response.ok) {

                throw new Error(
                    data.message ||
                    data.error ||
                    "Server error: " +
                    response.status
                );

            }


            if (!data.success) {

                throw new Error(
                    data.message ||
                    "The AI could not generate the test."
                );

            }


            if (
                !Array.isArray(
                    data.questions
                ) ||
                data.questions.length === 0
            ) {

                throw new Error(
                    "The AI response contains no questions."
                );

            }


            questions =
                data.questions;


            currentTestInfo = {

                filename:
                    data.filename ||
                    file.name,

                difficulty:
                    data.difficulty ||
                    difficulty.value,

                questionType:
                    data.question_type ||
                    questionType.value,

                questionCount:
                    questions.length

            };


            renderQuestions();


            testArea.style.display =
                "block";


            showStatus(
                "✅ " +
                questions.length +
                " questions generated successfully!",
                "success"
            );


            testArea.scrollIntoView({
                behavior: "smooth"
            });


        } catch (error) {

            console.error(
                "Generate error:",
                error
            );


            showStatus(
                "❌ " +
                error.message,
                "error"
            );

        }


        generateBtn.disabled =
            false;

        generateBtn.textContent =
            "Generate Test";

    }
);


/* ==================================================
   RENDER QUESTIONS
================================================== */

function renderQuestions() {

    questionsContainer.innerHTML =
        "";

    testFinished =
        false;


    questions.forEach(
        function(q, index) {

            const questionDiv =
                document.createElement(
                    "div"
                );

            questionDiv.className =
                "question";


            const title =
                document.createElement(
                    "div"
                );

            title.className =
                "question-title";


            title.textContent =
                "Question " +
                (index + 1) +
                ": " +
                String(
                    q.question || ""
                );


            questionDiv.appendChild(
                title
            );


            let options =
                q.options;


            if (
                typeof options ===
                "string"
            ) {

                try {

                    options =
                        JSON.parse(
                            options
                        );

                } catch (error) {

                    options = {};

                }

            }


            if (
                !options ||
                typeof options !==
                "object"
            ) {

                options = {};

            }


            if (
                Object.keys(options).length
                > 0
            ) {

                Object.keys(options).forEach(
                    function(letter) {

                        const option =
                            document.createElement(
                                "label"
                            );

                        option.className =
                            "option";


                        const input =
                            document.createElement(
                                "input"
                            );

                        input.type =
                            "radio";

                        input.name =
                            "question_" +
                            index;

                        input.value =
                            letter;


                        const text =
                            document.createElement(
                                "span"
                            );

                        text.textContent =
                            letter +
                            ". " +
                            String(
                                options[letter] ??
                                ""
                            );


                        option.appendChild(
                            input
                        );

                        option.appendChild(
                            text
                        );


                        questionDiv.appendChild(
                            option
                        );

                    }
                );

            } else {

                const input =
                    document.createElement(
                        "input"
                    );

                input.type =
                    "text";

                input.className =
                    "short-answer-input";

                input.id =
                    "short_" +
                    index;

                input.placeholder =
                    "Type your answer here...";


                questionDiv.appendChild(
                    input
                );

            }


            const answerBox =
                document.createElement(
                    "div"
                );

            answerBox.className =
                "answer-box";

            answerBox.id =
                "answer_" +
                index;


            questionDiv.appendChild(
                answerBox
            );


            questionsContainer.appendChild(
                questionDiv
            );

        }
    );

}


/* ==================================================
   FINISH GENERATED TEST
================================================== */

finishBtn.addEventListener(
    "click",
    function() {

        if (testFinished) {
            return;
        }


        if (!questions.length) {
            return;
        }


        let correct = 0;

        let answered = 0;


        const resultQuestions = [];


        questions.forEach(
            function(q, index) {

                const questionDiv =
                    questionsContainer
                        .children[index];


                const answerBox =
                    document.getElementById(
                        "answer_" +
                        index
                    );


                const topicName =
                    q.topic &&
                    String(q.topic).trim()
                        ? String(
                            q.topic
                        ).trim()
                        : "General";


                let questionCorrect =
                    false;

                let userAnswer =
                    "";


                let options =
                    q.options;


                if (
                    typeof options ===
                    "string"
                ) {

                    try {

                        options =
                            JSON.parse(
                                options
                            );

                    } catch (error) {

                        options = {};

                    }

                }


                if (
                    !options ||
                    typeof options !==
                    "object"
                ) {

                    options = {};

                }


                if (
                    Object.keys(options).length
                    > 0
                ) {

                    const selected =
                        document.querySelector(
                            'input[name="question_' +
                            index +
                            '"]:checked'
                        );


                    if (selected) {

                        answered++;

                        userAnswer =
                            selected.value;

                    }


                    const correctAnswer =
                        String(
                            q.answer || ""
                        )
                        .trim()
                        .toUpperCase();


                    const selectedAnswer =
                        selected
                            ? selected.value
                                .toUpperCase()
                            : null;


                    const optionElements =
                        questionDiv
                            .querySelectorAll(
                                ".option"
                            );


                    optionElements.forEach(
                        function(option) {

                            const input =
                                option.querySelector(
                                    "input"
                                );


                            input.disabled =
                                true;


                            if (
                                input.value
                                    .toUpperCase() ===
                                correctAnswer
                            ) {

                                option.classList.add(
                                    "correct"
                                );

                            }


                            if (
                                selectedAnswer &&
                                input.value
                                    .toUpperCase() ===
                                selectedAnswer &&
                                selectedAnswer !==
                                correctAnswer
                            ) {

                                option.classList.add(
                                    "wrong"
                                );

                            }

                        }
                    );


                    if (
                        selectedAnswer ===
                        correctAnswer
                    ) {

                        correct++;

                        questionCorrect =
                            true;

                    }


                    if (selectedAnswer) {

                        if (
                            selectedAnswer ===
                            correctAnswer
                        ) {

                            answerBox.textContent =
                                "✅ Correct! Answer: " +
                                correctAnswer;

                            answerBox.className =
                                "answer-box correct-answer";

                        } else {

                            answerBox.textContent =
                                "❌ Incorrect. Correct answer: " +
                                correctAnswer;

                            answerBox.className =
                                "answer-box wrong-answer";

                        }

                    } else {

                        answerBox.textContent =
                            "⚪ Not answered. Correct answer: " +
                            correctAnswer;

                        answerBox.className =
                            "answer-box wrong-answer";

                    }


                    answerBox.style.display =
                        "block";

                } else {

                    const input =
                        document.getElementById(
                            "short_" +
                            index
                        );


                    const userText =
                        input.value.trim();


                    userAnswer =
                        userText;


                    if (userText.length > 0) {
                        answered++;
                    }


                    input.disabled =
                        true;


                    const correctAnswer =
                        String(
                            q.answer || ""
                        ).trim();


                    const userLower =
                        userText.toLowerCase();


                    const correctLower =
                        correctAnswer.toLowerCase();


                    const isCorrect =
                        userText.length > 0 &&
                        (
                            userLower ===
                            correctLower ||

                            userLower.includes(
                                correctLower
                            ) ||

                            correctLower.includes(
                                userLower
                            )
                        );


                    if (isCorrect) {

                        correct++;

                        questionCorrect =
                            true;


                        answerBox.textContent =
                            "✅ Correct! Answer: " +
                            correctAnswer;

                        answerBox.className =
                            "answer-box correct-answer";

                    } else {

                        answerBox.textContent =
                            "❌ Incorrect. Correct answer: " +
                            correctAnswer;

                        answerBox.className =
                            "answer-box wrong-answer";

                    }


                    answerBox.style.display =
                        "block";

                }


                resultQuestions.push({

                    topic:
                        topicName,

                    correct:
                        questionCorrect,

                    userAnswer:
                        userAnswer,

                    correctAnswer:
                        String(
                            q.answer || ""
                        )

                });

            }
        );


        const total =
            questions.length;


        const percentage =
            Math.round(
                correct /
                total *
                100
            );


        score.textContent =
            correct +
            " / " +
            total;


        resultText.textContent =
            "You answered " +
            answered +
            " out of " +
            total +
            " questions. Score: " +
            percentage +
            "%";


        result.style.display =
            "block";


        testFinished =
            true;


        finishBtn.disabled =
            true;


        saveHistory({

            id:
                Date.now(),

            date:
                new Date().toISOString(),

            filename:
                currentTestInfo.filename,

            difficulty:
                currentTestInfo.difficulty,

            questionType:
                currentTestInfo.questionType,

            total:
                total,

            correct:
                correct,

            percentage:
                percentage,

            questions:
                resultQuestions

        });


        saveExamSection.style.display =
            "block";


        saveExamSection.scrollIntoView({
            behavior: "smooth"
        });

    }
);


/* ==================================================
   SAVE EXAM
================================================== */

saveExamBtn.addEventListener(
    "click",
    async function() {

        if (!examTitle.value.trim()) {

            showStatus(
                "Please enter an exam title.",
                "error"
            );

            examTitle.focus();

            return;

        }


        if (!subjectId.value) {

            showStatus(
                "Please select a subject.",
                "error"
            );

            subjectId.focus();

            return;

        }


        if (!questions.length) {

            showStatus(
                "There are no questions to save.",
                "error"
            );

            return;

        }


        saveExamBtn.disabled =
            true;

        saveExamBtn.textContent =
            "Saving Exam...";


        showStatus(
            "💾 Saving exam and questions to the shared question bank...",
            "loading"
        );


        const saveData = {

            title:
                examTitle.value.trim(),

            subject_id:
                Number(
                    subjectId.value
                ),

            grade:
                grade.value,

            topic:
                topic.value.trim(),

            exam_type:
                examType.value,

            year:
                examYear.value
                    ? Number(
                        examYear.value
                    )
                    : null,

            description:
                description.value.trim(),

            file_url:
                "",

            answer_url:
                "",

            difficulty:
                currentTestInfo.difficulty,

            question_type:
                currentTestInfo.questionType,

            questions:
                questions

        };


        try {

            const response =
                await fetch(
                    SAVE_EXAM_URL,
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                saveData
                            )
                    }
                );


            const rawText =
                await response.text();


            let data;


            try {

                data =
                    JSON.parse(
                        rawText
                    );

            } catch (error) {

                throw new Error(
                    "Server returned an invalid response."
                );

            }


            if (!response.ok) {

                throw new Error(
                    data.message ||
                    data.error ||
                    "Server error: " +
                    response.status
                );

            }


            if (!data.success) {

                throw new Error(
                    data.message ||
                    "Could not save the exam."
                );

            }


            showStatus(
                "✅ Exam saved successfully! Exam ID: " +
                data.exam_id,
                "success"
            );


            saveExamBtn.textContent =
                "✅ Exam Saved";

            saveExamBtn.disabled =
                true;


            loadLibrary();


        } catch (error) {

            console.error(
                "Save error:",
                error
            );


            showStatus(
                "❌ " +
                error.message,
                "error"
            );


            saveExamBtn.disabled =
                false;

            saveExamBtn.textContent =
                "💾 Save Exam";

        }

    }
);


/* ==================================================
   NEW TEST
================================================== */

newTestBtn.addEventListener(
    "click",
    function() {

        questions = [];

        testFinished =
            false;


        questionsContainer.innerHTML =
            "";

        result.style.display =
            "none";

        testArea.style.display =
            "none";

        saveExamSection.style.display =
            "none";

        status.style.display =
            "none";


        finishBtn.disabled =
            false;


        saveExamBtn.disabled =
            false;

        saveExamBtn.textContent =
            "💾 Save Exam";


        pdfFile.value =
            "";

        fileName.textContent =
            "";


        examTitle.value =
            "";

        subjectId.value =
            "";

        grade.value =
            "";

        topic.value =
            "";

        examType.value =
            "";

        examYear.value =
            "";

        description.value =
            "";


        window.scrollTo({

            top: 0,

            behavior: "smooth"

        });

    }
);


/* ==================================================
   CLEAR HISTORY
================================================== */

clearHistoryBtn.addEventListener(
    "click",
    function() {

        const history =
            getHistory();


        if (!history.length) {
            return;
        }


        const confirmed =
            confirm(
                "Are you sure you want to delete all test history?"
            );


        if (!confirmed) {
            return;
        }


        localStorage.removeItem(
            HISTORY_KEY
        );


        updateProgress();

    }
);


/* ==================================================
   PROGRESS
================================================== */

function updateProgress() {

    const history =
        getHistory();


    if (!history.length) {

        totalTests.textContent =
            "0";

        averageScore.textContent =
            "0%";

        totalQuestions.textContent =
            "0";


        weakAreaText.textContent =
            "Complete a test to discover your weakest areas.";


        topicStats.innerHTML =
            '<div class="no-history">' +
            'Complete a test to see your topic performance.' +
            '</div>';


        historyContainer.innerHTML =
            '<div class="no-history">' +
            'No tests completed yet.' +
            '</div>';


        return;

    }


    totalTests.textContent =
        history.length;


    let totalScore =
        0;

    let answeredQuestions =
        0;


    history.forEach(
        function(test) {

            totalScore +=
                Number(
                    test.percentage || 0
                );

            answeredQuestions +=
                Number(
                    test.total || 0
                );

        }
    );


    averageScore.textContent =
        Math.round(
            totalScore /
            history.length
        ) +
        "%";


    totalQuestions.textContent =
        answeredQuestions;


    const topicData = {};


    history.forEach(
        function(test) {

            if (
                !Array.isArray(
                    test.questions
                )
            ) {
                return;
            }


            test.questions.forEach(
                function(q) {

                    const topicName =
                        q.topic &&
                        String(
                            q.topic
                        ).trim()
                            ? String(
                                q.topic
                            ).trim()
                            : "General";


                    if (
                        !topicData[
                            topicName
                        ]
                    ) {

                        topicData[
                            topicName
                        ] = {

                            correct: 0,

                            total: 0

                        };

                    }


                    topicData[
                        topicName
                    ].total++;


                    if (
                        q.correct === true
                    ) {

                        topicData[
                            topicName
                        ].correct++;

                    }

                }
            );

        }
    );


    const topics =
        Object.keys(
            topicData
        );


    if (!topics.length) {

        weakAreaText.textContent =
            "Complete more tests to identify your weakest areas.";

        topicStats.innerHTML =
            '<div class="no-history">' +
            'Complete a test to see your topic performance.' +
            '</div>';

    } else {

        topics.sort(
            function(a, b) {

                const accuracyA =
                    topicData[a].correct /
                    topicData[a].total;

                const accuracyB =
                    topicData[b].correct /
                    topicData[b].total;

                return (
                    accuracyA -
                    accuracyB
                );

            }
        );


        const weakest =
            topics[0];


        const weakestAccuracy =
            Math.round(
                topicData[
                    weakest
                ].correct /
                topicData[
                    weakest
                ].total *
                100
            );


        weakAreaText.innerHTML =
            "Your current weakest area is " +
            "<strong>" +
            escapeHTML(
                weakest
            ) +
            "</strong> with " +
            "<strong>" +
            weakestAccuracy +
            "% accuracy</strong>.";


        topicStats.innerHTML =
            "";


        topics.forEach(
            function(topicName) {

                const data =
                    topicData[
                        topicName
                    ];


                const accuracy =
                    Math.round(
                        data.correct /
                        data.total *
                        100
                    );


                const row =
                    document.createElement(
                        "div"
                    );

                row.className =
                    "topic-row";


                row.innerHTML =

                    '<div class="topic-header">' +

                        '<span>' +
                            escapeHTML(
                                topicName
                            ) +
                        '</span>' +

                        '<span>' +
                            accuracy +
                            '%' +
                        '</span>' +

                    '</div>' +

                    '<div class="progress-bar">' +

                        '<div class="progress-fill" ' +
                        'style="width:' +
                        accuracy +
                        '%"></div>' +

                    '</div>' +

                    '<div style="font-size:13px;color:#777;margin-top:5px;">' +

                        data.correct +
                        ' correct out of ' +
                        data.total +

                    '</div>';


                topicStats.appendChild(
                    row
                );

            }
        );

    }


    historyContainer.innerHTML =
        "";


    history.forEach(
        function(test) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "history-item";


            const date =
                new Date(
                    test.date
                );


            const formattedDate =
                date.toLocaleDateString(
                    "en-US",
                    {
                        year: "numeric",
                        month: "short",
                        day: "numeric"
                    }
                );


            item.innerHTML =

                '<div class="history-top">' +

                    '<div class="history-file">' +
                        '📄 ' +
                        escapeHTML(
                            test.filename
                        ) +
                    '</div>' +

                    '<div class="history-score">' +
                        test.correct +
                        '/' +
                        test.total +
                        ' (' +
                        test.percentage +
                        '%)' +
                    '</div>' +

                '</div>' +

                '<div class="history-meta">' +

                    formattedDate +
                    ' · ' +
                    capitalize(
                        test.difficulty
                    ) +
                    ' · ' +
                    formatQuestionType(
                        test.questionType
                    ) +

                '</div>';


            historyContainer.appendChild(
                item
            );

        }
    );

}


/* ==================================================
   INITIALIZE
================================================== */

async function initializeApp() {

    updateProgress();

    await loadSubjects();

    await loadLibrary();

    console.log(
        "Text2Test AI frontend loaded successfully."
    );

}


initializeApp();

</script>

</body>

</html>
