// filter.js

// Utility Functions
function getElement(selector) {
    return document.querySelector(selector);
}

function getElements(selector) {
    return document.querySelectorAll(selector);
}

function removeElement(element) {
    if (element) {
        element.remove();
    }
}

// Delete Filter Group
function deleteFilterGroup(groupId) {
    const filterGroup = getElement(`#filter-group-${groupId}`);
    const logicDropdown = getElement(`#group-logic-${groupId}`);

    removeElement(filterGroup);
    removeElement(logicDropdown);
}

// Delete Filter Rule
function deleteFilter(filterId) {
    const filterRule = getElement(`#filter-rule-${filterId}`);
    removeElement(filterRule);
}

// Duplicate Filter Rule
function duplicateFilter(filterId) {
    const originalFilter = getElement(`#filter-field-${filterId}`).closest('.filter-rule');
    const newFilter = originalFilter.cloneNode(true);
    filterCount++;

    updateFilterIds(newFilter, filterId, filterCount);
    getElement('#filter-rules-container').appendChild(newFilter);
    addChangeEventToFilter(filterCount);
}

// Helper to update the IDs of duplicated filters
function updateFilterIds(newFilter, oldId, newId) {
    newFilter.querySelector(`#filter-field-${oldId}`).id = `filter-field-${newId}`;
    newFilter.querySelector(`#filter-operator-${oldId}`).id = `filter-operator-${newId}`;
    newFilter.querySelector(`#filter-input-${oldId}`).id = `filter-input-${newId}`;
    newFilter.querySelector(`#dropdownMenuButton-${oldId}`).id = `dropdownMenuButton-${newId}`;
}

// Add Filter Rule
function addFilterRule(logic = true) {
    filterCount++;
    const filterRulesContainer = getElement('#filter-rules-container');
    const logicDropdownHTML = createLogicDropdownHTML(logic, filterCount);
    const newFilterRuleHTML = createFilterRuleHTML(logicDropdownHTML, filterCount);

    const newFilterRule = document.createElement('div');
    newFilterRule.classList.add('row', 'filter-rule');
    newFilterRule.innerHTML = newFilterRuleHTML;
    filterRulesContainer.appendChild(newFilterRule);

    addChangeEventToFilter(filterCount);
}

// Add Filter Group
function addFilterGroup() {
    filterGroupCount++;
    const filterRulesContainer = getElement('#filter-rules-container');

    const logicDropdownHTML = `
        <div class="col-md-2 col-sm-12 mb-3" id="group-logic-${filterGroupCount}">
            <select name="group_filter_logic[]" class="form-control">
                <option value="and">AND</option>
                <option value="or">OR</option>
            </select>
        </div>
    `;

    const newFilterGroupHTML = `
        <div class="nested-group-rules" id="filter-group-rules-${filterGroupCount}"></div>
        <div class="row">
            <div class="col-md-2 col-sm-12">
                <button type="button" class="btn btn-secondary w-100" id="add-rule-to-group-${filterGroupCount}">Add Rule to Group</button>
            </div>
            <div class="col-md-2 col-sm-12">
                <div class="dropdown">
                    <button class="btn btn-light" type="button" id="dropdownMenuButton-${filterGroupCount}" data-bs-toggle="dropdown" aria-expanded="false">&bull;&bull;&bull;</button>
                    <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton-${filterGroupCount}">
                        <li><a class="dropdown-item" href="#" onclick="deleteFilterGroup(${filterGroupCount})">Remove Group</a></li>
                    </ul>
                </div>
            </div>
        </div>
    `;

    const newFilterGroup = document.createElement('div');
    newFilterGroup.classList.add('filter-group', 'nested-group');
    newFilterGroup.innerHTML = logicDropdownHTML + newFilterGroupHTML;

    filterRulesContainer.appendChild(newFilterGroup);

    getElement(`#add-rule-to-group-${filterGroupCount}`).addEventListener('click', function () {
        addFilterRuleInGroup(filterGroupCount);
    });
}

// Add Filter Rule in Group
function addFilterRuleInGroup(groupId) {
    filterCount++;
    const groupRulesContainer = getElement(`#filter-group-rules-${groupId}`);

    let logicDropdown = '';
    if (groupRulesContainer.children.length > 0) {
        logicDropdown = `
            <div class="col-md-2 col-sm-12 mb-3">
                <select id="group-filter-logic-${filterCount}" name="group_filter_logic[]" class="form-control">
                    <option value="and">AND</option>
                    <option value="or">OR</option>
                </select>
            </div>
        `;
    }

    const newRuleHTML = `
        ${logicDropdown}
        <div class="col-md-2 col-sm-12 mb-3">
            <select id="filter-field-${filterCount}" name="filter_field[]" class="form-control">
                <option value="">Pilih Filter</option>
                <option value="product_name" data-type="text">Nama Produk</option>
                <option value="category" data-type="text">Kategori</option>
                <option value="code" data-type="text">Kode Produk</option>
                <option value="storage" data-type="text">Tempat Barang</option>
                <option value="stock" data-type="number">Stok</option>
                <option value="stock_status" data-type="dropdown">Status Stok</option>
                <option value="created_at" data-type="date">Ditambahkan Pada</option>
                <option value="updated_at" data-type="date">Diperbaharui Pada</option>
            </select>
        </div>
        <div class="col-md-2 col-sm-12 mb-3">
            <select id="filter-operator-${filterCount}" name="filter_operator[]" class="form-control"></select>
        </div>
        <div class="col-md-2 col-sm-12 mb-3">
            <input type="text" id="filter-input-${filterCount}" name="filter_value[]" class="form-control" placeholder="Enter value">
        </div>
        <div class="col-md-2 col-sm-12 mb-3">
            <div class="dropdown">
                <button class="btn btn-light" type="button" id="dropdownMenuButton-${filterCount}" data-bs-toggle="dropdown" aria-expanded="false">&bull;&bull;&bull;</button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton-${filterCount}">
                    <li><a class="dropdown-item" href="#" onclick="deleteFilter(${filterCount})">Remove</a></li>
                </ul>
            </div>
        </div>
    `;

    const newRule = document.createElement('div');
    newRule.classList.add('row', 'filter-rule');
    newRule.innerHTML = newRuleHTML;

    groupRulesContainer.appendChild(newRule);
    addChangeEventToFilter(filterCount);
}

// Populate Operators based on Field Type
function populateOperators(filterId) {
    const selectedField = getElement(`#filter-field-${filterId}`);
    const fieldType = selectedField.options[selectedField.selectedIndex].getAttribute('data-type');
    const filterOperator = getElement(`#filter-operator-${filterId}`);
    const filterInputs = getElement(`#filter-input-${filterId}`);

    filterOperator.innerHTML = '';
    filterInputs.innerHTML = '';

    switch (fieldType) {
        case 'text':
            setTextFieldOperators(filterOperator, filterInputs);
            break;
        case 'number':
            setNumberFieldOperators(filterOperator, filterInputs);
            break;
        case 'dropdown':
            setDropdownFieldOperators(filterOperator, filterInputs);
            break;
        case 'date':
            setDateFieldOperators(filterOperator, filterInputs);
            break;
    }
}

// Utility Functions for Operators
function setTextFieldOperators(filterOperator, filterInputs) {
    filterOperator.innerHTML = `
        <option value="is">Is</option>
        <option value="is_not">Is Not</option>
        <option value="contains">Contains</option>
        <option value="does_not_contain">Does Not Contain</option>
        <option value="starts_with">Starts With</option>
        <option value="ends_with">Ends With</option>
        <option value="is_empty">Is Empty</option>
        <option value="is_not_empty">Is Not Empty</option>
    `;
    filterInputs.innerHTML = `<input type="text" name="filter_value[]" class="form-control" placeholder="Enter value">`;
}

function setNumberFieldOperators(filterOperator, filterInputs) {
    filterOperator.innerHTML = `
        <option value="=">=</option>
        <option value="!=">!=</option>
        <option value=">">></option>
        <option value="<"><</option>
        <option value=">=">>=</option>
        <option value="<="><=</option>
        <option value="is_empty">Is Empty</option>
        <option value="is_not_empty">Is Not Empty</option>
    `;
    filterInputs.innerHTML = `<input type="number" name="filter_value[]" class="form-control" placeholder="Enter value">`;
}

function setDropdownFieldOperators(filterOperator, filterInputs) {
    filterOperator.innerHTML = `
        <option value="is">Is</option>
        <option value="is_not">Is Not</option>
    `;
    filterInputs.innerHTML = `
        <select name="filter_value[]" class="form-control">
            <option value="available">Tersedia</option>
            <option value="unavailable">Tidak Tersedia</option>
        </select>
    `;
}

function setDateFieldOperators(filterOperator, filterInputs) {
    filterOperator.innerHTML = `
        <option value="is">Is</option>
        <option value="is_before">Is Before</option>
        <option value="is_after">Is After</option>
        <option value="is_between">Is Between</option>
        <option value="is_empty">Is Empty</option>
        <option value="is_not_empty">Is Not Empty</option>
    `;
    filterInputs.innerHTML = `
        <input type="date" name="filter_value_start[]" class="form-control mb-2" placeholder="Start Date">
        <input type="date" name="filter_value_end[]" class="form-control" placeholder="End Date" style="display:none;">
    `;

    filterOperator.addEventListener('change', function () {
        const endDateInput = getElement('input[name="filter_value_end[]"]');
        if (this.value === 'is_between') {
            endDateInput.style.display = 'block';
        } else {
            endDateInput.style.display = 'none';
        }
    });
}

// Form Validation
function validateFilterForm() {
    const fields = getElements('select[name="filter_field[]"]');
    const operators = getElements('select[name="filter_operator[]"]');
    const values = getElements('input[name="filter_value[]"], select[name="filter_value[]"]');

    let fieldMap = {};

    for (let i = 0; i < fields.length; i++) {
        const field = fields[i].value;
        const operator = operators[i].value;
        const value = values[i].value;

        if (!field || !operator || !value) {
            alert("Please complete all filter fields.");
            return false;
        }

        // Check for conflicting filters
        if (!fieldMap[field]) {
            fieldMap[field] = { operator, value };
        } else if (fieldMap[field].operator !== operator && fieldMap[field].operator.includes('<=') && operator.includes('>=')) {
            alert(`Conflicting filter found for ${field}. Please resolve the conflict.`);
            return false;
        }
    }

    return true;
}

// Initialize Events and Load Filter Settings
document.addEventListener('DOMContentLoaded', function () {
    getElement('#filter-icon').addEventListener('click', toggleFilterSection);
    getElement('#clear-filter').addEventListener('click', clearFilters);
    getElement('#add-filter-rule').addEventListener('click', addFilterRule);
    getElement('#add-filter-group').addEventListener('click', addFilterGroup);
    
    loadFilterSettings();
});

// Toggle filter section visibility
function toggleFilterSection() {
    const filterSection = getElement('#filter-inputs-section');
    filterSection.style.display = filterSection.style.display === "none" ? "block" : "none";
}

// Clear all filters
function clearFilters() {
    window.location.href = '{{ url_for("product_routes.get_productlist") }}';
}

// Save Filter Settings
function saveFilterSettings() {
    const filters = getElements('.filter-rule');
    let filterSettings = [];

    filters.forEach(filter => {
        let field = filter.querySelector('select[name="filter_field[]"]').value;
        let operator = filter.querySelector('select[name="filter_operator[]"]').value;
        let value = filter.querySelector('input[name="filter_value[]"]').value;
        filterSettings.push({ field, operator, value });
    });

    localStorage.setItem('filterSettings', JSON.stringify(filterSettings));
}

// Load Filter Settings
function loadFilterSettings() {
    const filterSettings = JSON.parse(localStorage.getItem('filterSettings'));
    if (filterSettings) {
        filterSettings.forEach(filter => {
            addFilterRule();
            // Apply saved values (this can be expanded to set field/operator/value)
        });
    }
}
