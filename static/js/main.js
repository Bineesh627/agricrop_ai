// AgriCrop AI - JavaScript Helper Utilities

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Preset options configuration for Recommendation Form
    const presets = {
        'rice': {
            n: 90, p: 42, k: 43, temp: 23.6, hum: 82.2, ph: 6.5, rain: 230, soil: 'Clayey', season: 'Kharif'
        },
        'maize': {
            n: 77, p: 48, k: 20, temp: 22.3, hum: 65.0, ph: 6.2, rain: 84, soil: 'Loamy', season: 'Kharif'
        },
        'chickpea': {
            n: 40, p: 68, k: 80, temp: 18.9, hum: 16.8, ph: 7.3, rain: 80, soil: 'Loamy', season: 'Rabi'
        },
        'grapes': {
            n: 23, p: 134, k: 200, temp: 23.8, hum: 81.9, ph: 6.0, rain: 70, soil: 'Loamy', season: 'Rabi'
        },
        'cotton': {
            n: 117, p: 46, k: 19, temp: 24.0, hum: 79.8, ph: 6.9, rain: 80, soil: 'Black', season: 'Kharif'
        },
        'apple': {
            n: 20, p: 134, k: 199, temp: 22.6, hum: 92.3, ph: 5.9, rain: 112, soil: 'Loamy', season: 'Whole Year'
        }
    };

    // Attach click listeners to preset pills
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const key = this.getAttribute('data-preset');
            if (presets[key]) {
                const data = presets[key];
                setInputValue('id_nitrogen', data.n);
                setInputValue('id_phosphorus', data.p);
                setInputValue('id_potassium', data.k);
                setInputValue('id_temperature', data.temp);
                setInputValue('id_humidity', data.hum);
                setInputValue('id_ph', data.ph);
                setInputValue('id_rainfall', data.rain);
                
                const soilSelect = document.getElementById('id_soil_type');
                if (soilSelect) soilSelect.value = data.soil;
                
                const seasonSelect = document.getElementById('id_season');
                if (seasonSelect) seasonSelect.value = data.season;

                // Highlight active preset
                document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active', 'bg-success', 'text-white'));
                this.classList.add('active', 'bg-success', 'text-white');
            }
        });
    });

    function setInputValue(id, val) {
        const input = document.getElementById(id);
        if (input) {
            input.value = val;
            input.classList.add('is-valid');
            setTimeout(() => input.classList.remove('is-valid'), 1200);
        }
    }
});
