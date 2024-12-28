// Fetch and display resume analysis results
async function fetchAnalysisResults() {
    try {
        const response = await fetch('/get-analysis-results');
        if (!response.ok) {
            throw new Error('Failed to fetch analysis results');
        }
        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error fetching results:', error);
        displayError('Failed to load analysis results. Please try again.');
    }
}

// Display the analysis results
function displayResults(result) {
    updateScore(result.ats_score);
    updateSkills(result.extracted_skills, result.missing_skills);
    updateFeedback(result.feedback_sections);
    updateMetrics(result.extracted_skills.length, result.missing_skills.length);
}

// Update ATS score and status
function updateScore(score) {
    const scoreElement = document.getElementById('atsScore');
    const statusElement = document.getElementById('scoreStatus');
    
    scoreElement.textContent = `${score}%`;
    
    // Determine status based on score
    let status = getScoreStatus(score);
    statusElement.textContent = status.text;
    statusElement.className = `score-status ${status.color}`;
}

// Helper function to determine score status
function getScoreStatus(score) {
    if (score >= 75) return { text: 'Excellent Match', color: 'text-green' };
    if (score >= 50) return { text: 'Good Match', color: 'text-yellow' };
    return { text: 'Needs Improvement', color: 'text-red' };
}

// Create and display skill tags
function updateSkills(extractedSkills, missingSkills) {
    const extractedContainer = document.getElementById('extractedSkills');
    const missingContainer = document.getElementById('missingSkills');
    
    extractedContainer.innerHTML = '';
    missingContainer.innerHTML = '';
    
    extractedSkills.forEach(skill => {
        extractedContainer.appendChild(createSkillTag(skill, 'extracted'));
    });
    
    missingSkills.forEach(skill => {
        missingContainer.appendChild(createSkillTag(skill, 'missing'));
    });
}

// Create individual skill tag
function createSkillTag(skill, type) {
    const tag = document.createElement('span');
    tag.className = `skill-tag ${type}`;
    tag.textContent = skill;
    return tag;
}

// Update feedback sections
function updateFeedback(feedbackSections) {
    const container = document.getElementById('feedbackContainer');
    container.innerHTML = '';
    
    Object.entries(feedbackSections).forEach(([section, feedback]) => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'feedback-item';
        feedbackItem.innerHTML = `
            <h3>${section}</h3>
            <p>${feedback}</p>
        `;
        container.appendChild(feedbackItem);
    });
}

// Update metrics display
function updateMetrics(foundCount, missingCount) {
    document.getElementById('skillsFoundCount').textContent = foundCount;
    document.getElementById('skillsMissingCount').textContent = missingCount;
}

// Display error message
function displayError(message) {
    const container = document.querySelector('.container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    container.prepend(errorDiv);
}

// Initialize the page and fetch results
document.addEventListener('DOMContentLoaded', fetchAnalysisResults);

// Add hover effects for skill tags
document.addEventListener('mouseover', (e) => {
    if (e.target.classList.contains('skill-tag')) {
        e.target.style.transform = 'translateY(-2px)';
        e.target.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
    }
});

document.addEventListener('mouseout', (e) => {
    if (e.target.classList.contains('skill-tag')) {
        e.target.style.transform = '';
        e.target.style.boxShadow = '';
    }
});