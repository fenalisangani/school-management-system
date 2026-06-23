(function () {
    'use strict';

    function fetchJson(url) {
        return fetch(url, { headers: { Accept: 'application/json' } }).then(function (r) {
            if (!r.ok) throw new Error('Request failed');
            return r.json();
        });
    }

    function setOptions(select, items, placeholder, valueKey) {
        if (!select) return;
        var current = select.value;
        select.innerHTML = '';
        var opt0 = document.createElement('option');
        opt0.value = '';
        opt0.textContent = placeholder || '---------';
        select.appendChild(opt0);
        items.forEach(function (item) {
            var opt = document.createElement('option');
            opt.value = item[valueKey || 'id'];
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
                setOptions(sectionSelect, [], 'Select a class/course first');
                sectionSelect.disabled = true;
                return;
            }
            sectionSelect.disabled = true;
            setOptions(sectionSelect, [], 'Loading divisions…');
            fetchJson('/classes/api/' + classId + '/sections/')
                .then(function (sections) {
                    if (!sections.length) {
                        setOptions(sectionSelect, [], 'No divisions — add one first');
                        sectionSelect.disabled = true;
                        return;
                    }
                    setOptions(
                        sectionSelect,
                        sections.map(function (s) { return { id: s.id, name: 'Division ' + s.name }; }),
                        'Select division / section'
                    );
                    sectionSelect.disabled = false;
                })
                .catch(function () {
                    setOptions(sectionSelect, [], 'Error loading divisions');
                    sectionSelect.disabled = false;
                });
        }

        classSelect.addEventListener('change', loadSections);
        if (classSelect.value) loadSections();
        else {
            setOptions(sectionSelect, [], 'Select a class/course first');
            sectionSelect.disabled = true;
        }
    }

    function bindClassMeta(classSelect, yearSelect, semesterSelect) {
        if (!classSelect) return;

        function syncMeta() {
            var classId = classSelect.value;
            if (!classId) {
                if (semesterSelect) {
                    setOptions(semesterSelect, [], 'Select a class/course first');
                    semesterSelect.disabled = true;
                }
                return;
            }
            fetchJson('/classes/api/' + classId + '/meta/')
                .then(function (meta) {
                    if (yearSelect && meta.academic_year_id) {
                        yearSelect.value = String(meta.academic_year_id);
                    }
                    if (semesterSelect) {
                        if (meta.uses_semesters && meta.semesters && meta.semesters.length) {
                            setOptions(semesterSelect, meta.semesters, 'Select semester', 'id');
                            semesterSelect.disabled = false;
                        } else {
                            setOptions(semesterSelect, [], 'Not applicable (school)');
                            semesterSelect.disabled = true;
                            semesterSelect.value = '';
                        }
                    }
                })
                .catch(function () { /* ignore */ });
        }

        classSelect.addEventListener('change', syncMeta);
        if (classSelect.value) syncMeta();
        else if (semesterSelect) {
            setOptions(semesterSelect, [], 'Not applicable (school)');
            semesterSelect.disabled = true;
        }
    }

    function bindInstitutionCascade(instSelect, classSelect, sectionSelect, semesterSelect, yearSelect) {
        if (!instSelect || !classSelect) return;

        function loadClasses() {
            var inst = instSelect.value;
            if (!inst) return;
            classSelect.disabled = true;
            setOptions(classSelect, [], 'Loading…');
            if (sectionSelect) {
                setOptions(sectionSelect, [], 'Select a class/course first');
                sectionSelect.disabled = true;
            }
            if (semesterSelect) {
                setOptions(semesterSelect, [], 'Not applicable');
                semesterSelect.disabled = true;
            }
            fetchJson('/classes/api/by-institution/' + inst + '/')
                .then(function (classes) {
                    if (!classes.length) {
                        setOptions(classSelect, [], 'No classes/courses — add one first');
                        return;
                    }
                    setOptions(
                        classSelect,
                        classes.map(function (c) { return { id: c.id, name: c.label || c.name }; }),
                        inst === 'college' ? 'Select course' : 'Select class / standard'
                    );
                    classSelect.disabled = false;
                    classSelect.label = inst === 'college' ? 'Course' : 'Class / Standard';
                })
                .catch(function () {
                    setOptions(classSelect, [], 'Error loading options');
                    classSelect.disabled = false;
                });
        }

        instSelect.addEventListener('change', loadClasses);
        if (classSelect.options.length <= 1 || !classSelect.value) {
            loadClasses();
        }
        bindClassSectionCascade(classSelect, sectionSelect);
        bindClassMeta(classSelect, yearSelect, semesterSelect);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var instField = document.getElementById('id_institution_type');
        var classField = document.getElementById('id_school_class');
        var sectionField = document.getElementById('id_section');
        var yearField = document.getElementById('id_academic_year');
        var semesterField = document.getElementById('id_semester');

        if (instField && classField) {
            bindInstitutionCascade(instField, classField, sectionField, semesterField, yearField);
        } else {
            if (classField && sectionField) {
                bindClassSectionCascade(classField, sectionField);
            }
            if (classField) {
                bindClassMeta(classField, yearField, semesterField);
            }
        }

        var bulkForm = document.getElementById('bulk-form');
        if (bulkForm) {
            var bulkInst = bulkForm.querySelector('#id_institution_type');
            var bulkClass = bulkForm.querySelector('#id_school_class');
            var bulkSection = bulkForm.querySelector('#id_section');
            var bulkSemester = bulkForm.querySelector('#id_semester');
            if (bulkInst && bulkClass) {
                bindInstitutionCascade(bulkInst, bulkClass, bulkSection, bulkSemester, null);
            } else if (bulkClass && bulkSection) {
                bindClassSectionCascade(bulkClass, bulkSection);
            }
        }
    });
})();
