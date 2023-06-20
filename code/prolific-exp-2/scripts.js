function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1)); // random index from 0 to i
        // swap elements array[i] and array[j]
        [array[i], array[j]] = [array[j], array[i]];
    }
}

async function createTrialPages(condition) {

    let trialPages = '';
    let num_trials = 12;

    // read stories from a json file
    let response = await fetch(`https://kanishkg.github.io/condition_${condition}_mcq_rerun_bwd.json`);
    // let response = await fetch(`condition_${condition}_mcq_rerun_bwd.json`);
    let trials = await response.json();
    shuffleArray(trials);

    window.trials = trials;

    for (let i = 1; i <= num_trials; i++) {

        trialPages += `
            <div id="trial-page-${i}" class="page d-none">
                <h4> Story </h4>
                <p> ${trials[i-1].story}</p>
                <h4> Question </h4>
                <p>${trials[i-1].question}</p>
                <h4> Answer Options </h4>
                <form>
                ${trials[i-1].answers_no_label.map((answer, j) => `
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="mcq-${i}" id="mcq-${i}-${j}" value="${j}">
                    <label class="form-check-label" for="mcq-${i}-${j}">${answer}</label>
                </div>
                `).join('')}
                </form>
            </div>`;
    }
    // add trial pages to the html
    var $trialPages = $("#trial-pages");
    $trialPages.append(trialPages);
}


$(document).ready(function () {
    
    let surveyData = {};
    surveyData.prolificPid = getUrlParameter("participant_id");
    surveyData.studyId = getUrlParameter("experiment_id");
    surveyData.condition = getUrlParameter("condition");

    createTrialPages(surveyData.condition).then(() => {


    let currentPage = 0;
    let totalPages = $(".page").length;
    let progressStep = 100 / totalPages;


    console.log(surveyData);
    function updateProgressBar() {
        let progress = progressStep * (currentPage + 1);
        $("#progress-bar").css("width", progress + "%").attr("aria-valuenow", progress);
    }


    function showPage(index) {
        $(".page").addClass("d-none");
        $(".page:eq(" + index + ")").removeClass("d-none");
        updateProgressBar();

        if (index === totalPages - 1) { // Check if it's the last page (exit survey)
            $("#next-btn").addClass("d-none");
            $("#submit-btn").removeClass("d-none");
        } else {
            $("#next-btn").removeClass("d-none");
            $("#submit-btn").addClass("d-none");
        }
    }

    function validateComprehensionTest() {
        // Check if the correct answers are selected
        const correctAnswers = {
            "comprehension-1": "false",
            "comprehension-2": "true",
            "comprehension-3": "false",
            "comprehension-4": "false",
            "comprehension-5": "false"
        };
    
        for (const question in correctAnswers) {
            const selectedAnswer = $(`input[name="${question}"]:checked`).val();
            if (selectedAnswer !== correctAnswers[question]) {
                return false;
            }
        }
    
        return true;
    }

    function submitExitSurvey() {
        // Gather trial page answers
        surveyData.trialPages = {};
        for (let i = 1; i <= 12; i++) {
            let trialData = window.trials[i-1];
            surveyData.trialPages[`trial${i}`] = {
                selected_answer_idx: $('input[name="mcq-' + i + '"]:checked').val(),
                story: trialData.story,
                question: trialData.question,
                answers: trialData.answers,
                answers_no_label: trialData.answers_no_label,
                true_labels: trialData.true_labels,
                data_source: trialData.data_source,
                id: trialData.id,
            };
        }

        // Gather exit survey answers
        // Replace 'input1', 'input2', etc. with the actual names or IDs of your input fields in the exit survey
        surveyData.exitSurvey = {
            age: $("#age").val(),
            gender: $("#gender").val(),
            race: $("#race").val(),
            ethnicity: $("#ethnicity").val(),
            // Add more input fields as needed
        };
    
        proliferate.submit(surveyData); // Uncomment this line when you're ready to use Proliferate
        // Show a thank you message or redirect to a thank you page
        // alert("Thank you for completing the survey!");
    }
    
    $("#submit-btn").click(function () {
        // Check if all the demographic fields have been filled
        if($("#age").val() && $("#gender").val() && $("#race").val() && $("#ethnicity").val()){
            if ($("#age").val() < 18 || $("#age").val() > 120) {
                alert("Please enter a valid age between 18 and 120.");
            }
            else{
                submitExitSurvey();
            }
        }
        // Check if age is between 18 and 120

         else {
            alert("Please fill out all the demographic fields.");
        }
    });

    function goToNextPage() {
        currentPage++;
        if (currentPage === totalPages) {
            $("#next-btn").prop("disabled", true);
        }
        if (currentPage > 0) {
            $("#prev-btn").removeClass("d-none");
        }
        showPage(currentPage);
        $("#next-btn").prop("disabled", true);
    }

    function goToPrevPage() {
        currentPage--;
        if (currentPage === 0) {
            $("#prev-btn").addClass("d-none");
        }
        if (currentPage < totalPages) {
            $("#next-btn").prop("disabled", false);
        }
        showPage(currentPage);
    }

    $("#next-btn").click(function () {
        if (currentPage === 0) {
            goToNextPage();
        } else if (currentPage === 5) {
            if (validateComprehensionTest()) {
                goToNextPage();
            } else {
                alert("Please answer the comprehension test questions correctly.");
            }
        } else {
            goToNextPage();
        }
        updateNextButtonState();
    });

    $("#prev-btn").click(function () {
        goToPrevPage();
        updateNextButtonState();
    });

    function checkAllAnswered() {
        let allAnswered = true;
        // Get the form on the current page
        let currentForm = $(`.page:eq(${currentPage}) form`);
    
        // Check if the form has a selected answer
        if (!currentForm.find('input[type="radio"]').is(':checked')) {
            allAnswered = false;
        }
        
        return allAnswered;
    }
    
    function updateNextButtonState() {
        // Get all input elements on the current page
        if (currentPage === 0 && !$("#consent-checkbox").is(":checked")) {
            $("#next-btn").prop("disabled", true);
        }
        else if (currentPage === 0 && $("#consent-checkbox").is(":checked")){
            $("#next-btn").prop("disabled", false);
        } 
        else if (currentPage >= 1 && currentPage <= 5) {
            $("#next-btn").prop("disabled", false);
        }
        else if (currentPage >= 5) {
            if (checkAllAnswered()) {
                $("#next-btn").prop("disabled", false);
            } else {
                $("#next-btn").prop("disabled", true);
            }
        }
    }

    $(document).on('click', 'input[type="radio"]', updateNextButtonState); 

    showPage(currentPage);
    updateNextButtonState();
    $("#consent-checkbox").change(function () {
        updateNextButtonState();
    });
});
});
