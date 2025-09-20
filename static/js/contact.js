document.addEventListener('DOMContentLoaded', function() {
    // Handle contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitContactForm();
        });
    }
    
    function submitContactForm() {
        clearErrorMessages();
        
        // Get form data
        const nameInput = document.getElementById('contactName');
        const emailInput = document.getElementById('contactEmail');
        const messageInput = document.getElementById('contactMessage');
        
        const name = nameInput.value.trim();
        const email = emailInput.value.trim();
        const message = messageInput.value.trim();
        
        // Validate form
        let isValid = true;
        
        if (!name) {
            showErrorMessage(nameInput, 'Please enter your name');
            isValid = false;
        } else if (name.length < 2) {
            showErrorMessage(nameInput, 'Name must be at least 2 characters');
            isValid = false;
        }
        
        if (!email) {
            showErrorMessage(emailInput, 'Please enter your email');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showErrorMessage(emailInput, 'Please enter a valid email address');
            isValid = false;
        }
        
        if (!message) {
            showErrorMessage(messageInput, 'Please enter your message');
            isValid = false;
        } else if (message.length < 10) {
            showErrorMessage(messageInput, 'Message must be at least 10 characters');
            isValid = false;
        }
        
        if (!isValid) {
            return;
        }
        
        // Show loading indicator
        const submitBtn = document.getElementById('submitContact');
        const submitText = document.getElementById('contactSubmitText');
        const loadingSpinner = document.getElementById('contactLoadingSpinner');
        
        submitText.style.display = 'none';
        loadingSpinner.classList.remove('d-none');
        submitBtn.disabled = true;
        
        // Get CSRF token
        const csrfToken = contactForm.querySelector('input[name="csrf_token"]').value;
        
        // Submit form via AJAX
        fetch('/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'csrf_token': csrfToken,
                'name': name,
                'email': email,
                'message': message
            })
        })
        .then(response => response.json())
        .then(data => {
            submitText.style.display = 'inline';
            loadingSpinner.classList.add('d-none');
            submitBtn.disabled = false;
            
            if (data.success) {
                // Clear the form
                contactForm.reset();
                
                // Show success message
                createAlert('success', 'Thank you for your message! We\'ll get back to you soon.');
            } else {
                // Handle validation errors
                if (data.errors) {
                    for (const field in data.errors) {
                        const inputId = 'contact' + field.charAt(0).toUpperCase() + field.slice(1);
                        const inputElement = document.getElementById(inputId);
                        if (inputElement) {
                            showErrorMessage(inputElement, data.errors[field][0]);
                        }
                    }
                } else {
                    createAlert('danger', 'An error occurred. Please try again.');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            submitText.style.display = 'inline';
            loadingSpinner.classList.add('d-none');
            submitBtn.disabled = false;
            createAlert('danger', 'An error occurred. Please try again.');
        });
    }
    
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email.toLowerCase());
    }
});