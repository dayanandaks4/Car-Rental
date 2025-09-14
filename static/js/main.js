// Main JavaScript for Rental App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle browser back/forward navigation
    window.addEventListener('popstate', function(event) {
        // Reload the page to ensure proper state
        location.reload();
    });

    // Auto-refresh vehicle availability every 30 seconds
    if (window.location.pathname.includes('vehicle-selection') || window.location.pathname.includes('my-rentals')) {
        setInterval(refreshVehicleAvailability, 30000);
    }

    // Vehicle selection functionality
    const vehicleCheckboxes = document.querySelectorAll('.vehicle-checkbox');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const proceedBtn = document.getElementById('proceedBtn');

    if (vehicleCheckboxes.length > 0) {
        // Handle individual checkbox changes
        vehicleCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSelection);
        });

        // Handle select all button
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', function() {
                const allChecked = Array.from(vehicleCheckboxes).every(cb => cb.checked);
                vehicleCheckboxes.forEach(checkbox => {
                    checkbox.checked = !allChecked;
                });
                updateSelection();
            });
        }

        // Handle proceed button
        if (proceedBtn) {
            proceedBtn.addEventListener('click', function() {
                const selectedVehicles = Array.from(vehicleCheckboxes)
                    .filter(cb => cb.checked)
                    .map(cb => cb.value);
                
                if (selectedVehicles.length === 0) {
                    alert('Please select at least one vehicle');
                    return;
                }

                // Create form and submit
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/rental-details';

                selectedVehicles.forEach(vehicleId => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'selected_vehicles';
                    input.value = vehicleId;
                    form.appendChild(input);
                });

                document.body.appendChild(form);
                form.submit();
            });
        }
    }

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    const vehicleTypeSelect = document.getElementById('vehicleTypeSelect');
    
    if (searchInput || vehicleTypeSelect) {
        const searchVehicles = debounce(function() {
            const searchTerm = searchInput ? searchInput.value : '';
            const vehicleType = vehicleTypeSelect ? vehicleTypeSelect.value : '';
            
            fetch(`/api/vehicles?search=${encodeURIComponent(searchTerm)}&type=${encodeURIComponent(vehicleType)}`)
                .then(response => response.json())
                .then(vehicles => {
                    updateVehicleDisplay(vehicles);
                })
                .catch(error => {
                    console.error('Error searching vehicles:', error);
                });
        }, 300);

        if (searchInput) {
            searchInput.addEventListener('input', searchVehicles);
        }
        if (vehicleTypeSelect) {
            vehicleTypeSelect.addEventListener('change', searchVehicles);
        }
    }

    // Date validation for rental form
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    
    if (startDateInput && endDateInput) {
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;

        startDateInput.addEventListener('change', function() {
            const startDate = new Date(this.value);
            const minEndDate = new Date(startDate);
            minEndDate.setDate(minEndDate.getDate() + 1);
            endDateInput.min = minEndDate.toISOString().split('T')[0];
            
            if (endDateInput.value && new Date(endDateInput.value) <= startDate) {
                endDateInput.value = '';
            }
        });

        endDateInput.addEventListener('change', function() {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(this.value);
            
            if (endDate <= startDate) {
                alert('End date must be after start date');
                this.value = '';
            }
        });
    }

    // Calculate total price
    const priceInputs = document.querySelectorAll('.price-input');
    if (priceInputs.length > 0) {
        priceInputs.forEach(input => {
            input.addEventListener('change', calculateTotalPrice);
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

function updateSelection() {
    const vehicleCheckboxes = document.querySelectorAll('.vehicle-checkbox');
    const selectedCount = Array.from(vehicleCheckboxes).filter(cb => cb.checked).length;
    const selectAllBtn = document.getElementById('selectAllBtn');
    const proceedBtn = document.getElementById('proceedBtn');

    if (selectAllBtn) {
        selectAllBtn.textContent = selectedCount === vehicleCheckboxes.length ? 'Deselect All' : 'Select All';
    }

    if (proceedBtn) {
        proceedBtn.disabled = selectedCount === 0;
        proceedBtn.textContent = selectedCount > 0 ? `Proceed with ${selectedCount} vehicle(s)` : 'Select vehicles to proceed';
    }
}

function updateVehicleDisplay(vehicles) {
    const vehicleContainer = document.getElementById('vehicleContainer');
    if (!vehicleContainer) return;

    vehicleContainer.innerHTML = '';
    
    if (vehicles.length === 0) {
        vehicleContainer.innerHTML = '<div class="col-12 text-center py-5"><h4>No vehicles found</h4></div>';
        return;
    }

    vehicles.forEach(vehicle => {
        const vehicleCard = createVehicleCard(vehicle);
        vehicleContainer.appendChild(vehicleCard);
    });
}

function createVehicleCard(vehicle) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';
    
    col.innerHTML = `
        <div class="vehicle-card">
            <div class="vehicle-image" style="background-image: url('${vehicle.image_url}')"></div>
            <div class="vehicle-info">
                <h5 class="vehicle-name">${vehicle.name}</h5>
                <p class="vehicle-model">${vehicle.model}</p>
                <div class="vehicle-specs">
                    <div class="spec-item">
                        <div class="spec-label">Mileage</div>
                        <div class="spec-value">${vehicle.mileage}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Type</div>
                        <div class="spec-value">${vehicle.vehicle_type.toUpperCase()}</div>
                    </div>
                </div>
                <div class="price">$${vehicle.price_per_day}/day</div>
                <div class="form-check">
                    <input class="form-check-input vehicle-checkbox" type="checkbox" value="${vehicle.id}" id="vehicle${vehicle.id}">
                    <label class="form-check-label" for="vehicle${vehicle.id}">
                        Select for rental
                    </label>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

function calculateTotalPrice() {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const totalPriceElement = document.getElementById('totalPrice');
    
    if (!startDateInput || !endDateInput || !totalPriceElement) return;
    
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);
    
    if (startDate && endDate && endDate > startDate) {
        const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        const pricePerDay = parseFloat(document.getElementById('pricePerDay').value) || 0;
        const total = days * pricePerDay;
        
        totalPriceElement.textContent = `$${total.toFixed(2)}`;
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility functions
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div>';
}

function hideLoading(element, content) {
    element.innerHTML = content;
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Refresh vehicle availability
function refreshVehicleAvailability() {
    fetch('/api/vehicles')
        .then(response => response.json())
        .then(vehicles => {
            updateVehicleAvailability(vehicles);
        })
        .catch(error => {
            console.error('Error refreshing vehicle availability:', error);
        });
}

// Update vehicle availability in real-time
function updateVehicleAvailability(vehicles) {
    const vehicleCards = document.querySelectorAll('.vehicle-card');
    vehicleCards.forEach(card => {
        const checkbox = card.querySelector('.vehicle-checkbox');
        const vehicleId = parseInt(checkbox.value);
        const vehicle = vehicles.find(v => v.id === vehicleId);
        
        if (vehicle && !vehicle.is_available) {
            card.style.opacity = '0.6';
            checkbox.disabled = true;
            checkbox.checked = false;
            const statusBadge = card.querySelector('.availability-status') || createStatusBadge();
            statusBadge.textContent = 'Rented';
            statusBadge.className = 'badge bg-danger availability-status';
        } else if (vehicle && vehicle.is_available) {
            card.style.opacity = '1';
            checkbox.disabled = false;
            const statusBadge = card.querySelector('.availability-status');
            if (statusBadge) {
                statusBadge.textContent = 'Available';
                statusBadge.className = 'badge bg-success availability-status';
            }
        }
    });
}

// Create status badge for vehicles
function createStatusBadge() {
    const badge = document.createElement('span');
    badge.className = 'badge bg-success availability-status';
    badge.textContent = 'Available';
    return badge;
}

// Enhanced error handling
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Enhanced success handling
function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// Loading indicator functions
function showLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.classList.add('show');
    }
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.classList.remove('show');
    }
}

// Enhanced form submission with loading
function enhanceFormSubmissions() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoading();
        });
    });
}

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function() {
    enhanceFormSubmissions();
    
    // Hide loading indicator after page load
    hideLoading();
});

// Hide loading on page load
window.addEventListener('load', function() {
    hideLoading();
});
