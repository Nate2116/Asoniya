
// Store selections in localStorage to persist across pages
const selections = {
    destinations: [],
    attractions: [],
    accommodations: [], 
    travelAgencies: [],
    carRentals: []
};

function toggleSelection(type, id, element) {
    const index = selections[type].indexOf(id);
    
    if (index === -1) {
        selections[type].push(id);
        element.classList.add('selected');
    } else {
        selections[type].splice(index, 1);
        element.classList.remove('selected');
    }
    
    localStorage.setItem('tripSelections', JSON.stringify(selections));
    updateProgress();
}

function updateProgress() {
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;
    
    let progress = 0;
    if (selections.destinations.length > 0) progress += 25;
    if (selections.accommodations.length > 0) progress += 25;
    if (selections.travelAgencies.length > 0) progress += 25;
    if (selections.carRentals.length > 0) progress += 25;
    
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
}

function loadSelections() {
    const saved = localStorage.getItem('tripSelections');
    if (saved) {
        Object.assign(selections, JSON.parse(saved));
        highlightSelectedItems();
        updateProgress();
    }
}

function highlightSelectedItems() {
    for (const type in selections) {
        selections[type].forEach(id => {
            const element = document.querySelector(`[data-id="${id}"]`);
            if (element) element.classList.add('selected');
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', loadSelections);
