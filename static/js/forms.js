(function () {
    'use strict';

    function fetchJson(url) {
        return fetch(url, { headers: { Accept: 'application/json' } }).then(function (r) {
            if (!r.ok) throw new Error('Request failed');
            return r.json();
        });
    }

    function setOptions(select, items, placeholder) {
        var current = select.value;
        select.innerHTML = '';
        var opt0 = document.createElement('option');
        opt0.value = '';
        opt0.textContent = placeholder || '---------';
        select.appendChild(opt0);
        items.forEach(function (item) {
            var opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.name || item.label;
            select.appendChild(opt);
        });
        if (current) select.value = current;
    }

    function bindClassSectionCascade(classSelect, sectionSelect) {
        if (!classSelect || !sectionSelect) return;

        function loadSections() {
            var classId = classSelect.value;
            if (!classId) {
                setOptions(sectionSelect, [], 'Select a class first');
                sectionSelect.disabled = true;
                return;
            }
            sectionSelect.disabled = true;
            setOptions(sectionSelect, [], 'Loading sections…');
            fetchJson('/classes/api/' + classId + '/sections/')
                .then(function (sections) {
                    if (!sections.length) {
                        setOptions(sectionSelect, [], 'No sections — add one first');
                        sectionSelect.disabled = true;
                        return;
                    }
                    setOptions(
                        sectionSelect,
                        sections.map(function (s) { return { id: s.id, name: 'Section ' + s.name }; }),
                        'Select section'
                    );
                    sectionSelect.disabled = false;
                })
                .catch(function () {
                    setOptions(sectionSelect, [], 'Error loading sections');
                    sectionSelect.disabled = false;
                });
        }

        classSelect.addEventListener('change', loadSections);
        // Initialise the placeholder so it's clear the section depends on the class.
        if (classSelect.value) loadSections();
        else {
            setOptions(sectionSelect, [], 'Select a class first');
            sectionSelect.disabled = true;
        }
    }

    function bindClassAcademicYear(classSelect, yearSelect) {
        if (!classSelect || !yearSelect) return;

        function syncYear() {
            var classId = classSelect.value;
            if (!classId) return;
            fetchJson('/classes/api/' + classId + '/meta/')
                .then(function (meta) {
                    if (meta.academic_year_id) {
                        yearSelect.value = String(meta.academic_year_id);
                    }
                })
                .catch(function () { /* ignore */ });
        }

        classSelect.addEventListener('change', syncYear);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var classField = document.getElementById('id_school_class');
        var sectionField = document.getElementById('id_section');
        var yearField = document.getElementById('id_academic_year');

        if (classField && sectionField) {
            bindClassSectionCascade(classField, sectionField);
        }
        if (classField && yearField) {
            bindClassAcademicYear(classField, yearField);
        }

        var bulkClass = document.querySelector('#bulk-form #id_school_class');
        var bulkSection = document.querySelector('#bulk-form #id_section');
        if (bulkClass && bulkSection) {
            bindClassSectionCascade(bulkClass, bulkSection);
        }
    });
})();
