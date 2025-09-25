document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#review-form');
  const reviewsContainer = document.querySelector('#reviews-container');
  const alertBox = document.querySelector('#review-alert');

  function loadReviews() {
    fetch('/reviews')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          reviewsContainer.innerHTML = '';
          data.reviews.forEach(review => {
          const card = `
            <div class="col">
              <div class="card h-100 shadow-sm border-0">
                <div class="card-body">
                  <h5 class="card-title">${review.name}</h5>
                  <p class="card-text">${review.comment}</p>
                  <div class="text-warning mb-2">
                    ${review.rating} / 5
                  </div>
                  <small class="text-muted">${review.date}</small>
                </div>
              </div>
            </div>
          `;
            reviewsContainer.innerHTML += card;
          });
        }
      });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(form);

      if (!formData.get('rating')) {
        alertBox.classList.remove('d-none', 'alert-success');
        alertBox.classList.add('alert-danger');
        alertBox.innerText = 'Please select a rating.';
        return;
      }

      fetch('/reviews', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alertBox.classList.remove('d-none', 'alert-danger');
          alertBox.classList.add('alert-success');
          alertBox.innerText = 'Thank you for your review!';
          form.reset();
          loadReviews();
        } else {
          alertBox.classList.remove('d-none', 'alert-success');
          alertBox.classList.add('alert-danger');
          alertBox.innerText = data.errors?.duplicate || data.errors?.form || 'Please fill in all fields.';
        }
      })
      .catch(() => {
        alertBox.classList.remove('d-none', 'alert-success');
        alertBox.classList.add('alert-danger');
        alertBox.innerText = 'Network error. Please try again.';
      });
    });
  }

  loadReviews();
});
