const featureSelect = document.getElementById("featureSelect");
const inputText = document.getElementById("inputText");
const characterCount = document.getElementById("characterCount");
const clearButton = document.getElementById("clearButton");
const generateButton = document.getElementById("generateButton");
const resultCard = document.getElementById("resultCard");
let activeController = null;

const endpoints = {
    qa: "/qa",
    explain: "/explain",
    quiz: "/quiz",
    summary: "/summarize",
    recommendations: "/learn/recommendations",
};

const resultKeys = {
    qa: "answer",
    explain: "explanation",
    quiz: "quiz",
    summary: "summary",
    recommendations: "recommendations",
};

const resultLabels = {
    qa: "Answer",
    explain: "Explanation",
    quiz: "Practice quiz",
    summary: "Summary",
    recommendations: "Learning path",
};

function updateCount() {
    characterCount.textContent = `${inputText.value.length} / ${inputText.maxLength}`;
}

function appendText(parent, value) {
    const paragraph = document.createElement("p");
    paragraph.textContent = value;
    parent.appendChild(paragraph);
}

function renderHeader(title) {
    const header = document.createElement("div");
    header.className = "result-header";

    const heading = document.createElement("div");
    const label = document.createElement("span");
    label.className = "result-label";
    label.textContent = "RESULT";
    const titleElement = document.createElement("h3");
    titleElement.textContent = title;
    heading.append(label, titleElement);

    const button = document.createElement("button");
    button.className = "copy-button";
    button.type = "button";
    button.textContent = "Copy";
    button.addEventListener("click", () => navigator.clipboard.writeText(resultCard.innerText));

    header.append(heading, button);
    resultCard.appendChild(header);
}

function renderText(value) {
    const content = document.createElement("div");
    content.className = "text-result";
    const text = String(value || "No response returned.");
    text.split(/\n+/).filter(Boolean).forEach((line) => appendText(content, line));
    resultCard.appendChild(content);
}

function renderQuiz(questions) {
    questions.forEach((item, questionIndex) => {
        const questionCard = document.createElement("article");
        questionCard.className = "quiz-question";

        const heading = document.createElement("h4");
        heading.textContent = `${questionIndex + 1}. ${item.question}`;
        questionCard.appendChild(heading);

        const options = document.createElement("ol");
        options.className = "quiz-options";
        (item.options || []).forEach((option) => {
            const optionItem = document.createElement("li");
            optionItem.textContent = option;
            options.appendChild(optionItem);
        });
        questionCard.appendChild(options);

        const answer = document.createElement("div");
        answer.className = "answer-box";
        const correctOption = item.options?.[item.answer] || item.options?.find((option) => String(option) === String(item.correct_answer)) || "See the explanation.";
        answer.textContent = `Answer: ${correctOption}${item.explanation ? ` — ${item.explanation}` : ""}`;
        questionCard.appendChild(answer);
        resultCard.appendChild(questionCard);
    });
}

function renderRecommendations(items) {
    items.forEach((item, index) => {
        const card = document.createElement("article");
        card.className = "quiz-question";

        const heading = document.createElement("h4");
        heading.textContent = `${index + 1}. ${item.title}`;
        card.appendChild(heading);

        const meta = document.createElement("div");
        meta.className = "result-label";
        meta.textContent = `${item.resource_type || "Learning resource"} · ${item.estimated_minutes || 30} min`;
        card.appendChild(meta);

        const description = document.createElement("div");
        description.className = "text-result";
        appendText(description, item.description || "");
        card.appendChild(description);
        resultCard.appendChild(card);
    });
}

function renderResult(feature, payload) {
    resultCard.replaceChildren();
    resultCard.classList.remove("hidden");
    renderHeader(resultLabels[feature]);
    const result = payload[resultKeys[feature]];

    if (feature === "quiz" && Array.isArray(result)) {
        renderQuiz(result);
    } else if (feature === "recommendations" && Array.isArray(result)) {
        renderRecommendations(result);
    } else {
        renderText(result);
    }
}

function renderError(message) {
    resultCard.replaceChildren();
    resultCard.classList.remove("hidden");
    const error = document.createElement("div");
    error.className = "error-box";
    error.textContent = message;
    resultCard.appendChild(error);
}

async function generate() {
    if (activeController) {
        return;
    }

    const value = inputText.value.trim();
    if (!value) {
        renderError("Enter a question, topic, or passage first.");
        inputText.focus();
        return;
    }

    const feature = featureSelect.value;
    const controller = new AbortController();
    activeController = controller;
    generateButton.disabled = true;
    generateButton.textContent = "Generating";
    resultCard.classList.add("hidden");

    try {
        const response = await fetch(endpoints[feature], {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: value }),
            signal: controller.signal,
        });
        const contentType = response.headers.get("content-type") || "";
        const payload = contentType.includes("application/json")
            ? await response.json()
            : null;
        if (!response.ok) {
            const detail = payload?.detail;
            throw new Error(
                typeof detail === "string"
                    ? detail
                    : "The request could not be completed.",
            );
        }
        if (!payload) {
            throw new Error("The server returned an invalid response.");
        }
        if (controller === activeController) {
            renderResult(feature, payload);
        }
    } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
            return;
        }
        if (controller === activeController) {
            renderError(error instanceof Error ? error.message : "The request could not be completed.");
        }
    } finally {
        if (controller === activeController) {
            activeController = null;
            generateButton.disabled = false;
            generateButton.textContent = "Generate";
        }
    }
}

inputText.addEventListener("input", updateCount);
inputText.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        generate();
    }
});
clearButton.addEventListener("click", () => {
    if (activeController) {
        activeController.abort();
        activeController = null;
        generateButton.disabled = false;
        generateButton.textContent = "Generate";
    }
    inputText.value = "";
    resultCard.classList.add("hidden");
    updateCount();
    inputText.focus();
});
generateButton.addEventListener("click", generate);
