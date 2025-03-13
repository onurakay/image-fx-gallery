var galleryImages = Array.from(document.querySelectorAll('.img-square'));
var currentIndex = 0;

function updateModalFromElement(el) {
  var imageSrc = el.getAttribute('data-image');
  var prompt = el.getAttribute('data-prompt');
  var seed = el.getAttribute('data-seed');
  var imageId = el.getAttribute('data-imageid');
  var createdAt = el.getAttribute('data-created');
  var imageFile = el.getAttribute('data-imagefile');
  var tags = JSON.parse(el.getAttribute('data-tags'));
  var aspectRatio = el.getAttribute('data-aspect_ratio');

  var modalImage = document.getElementById('modalImage');
  modalImage.src = imageSrc;

  if (aspectRatio === "6:11" || aspectRatio === "7:10") {
    modalImage.style.height = "800px";
  } else {
    modalImage.style.height = ""; //
  }

  document.getElementById('modalPrompt').textContent = prompt;
  document.getElementById('modalSeed').textContent = seed;
  document.getElementById('modalImageId').textContent = imageId;
  document.getElementById('modalCreatedAt').textContent = createdAt;
  modalImage.setAttribute('data-imagefile', imageFile);

  var modalTags = document.getElementById('modalTags');
  modalTags.innerHTML = '';
  if (tags.length > 0) {
    tags.forEach(function (tag) {
      var pill = document.createElement('span');
      pill.className = 'badge rounded-pill bg-primary me-1 tag-pill';
      pill.style.cursor = 'pointer';
      pill.setAttribute('data-tag', tag);
      pill.textContent = tag;

      var cross = document.createElement('button');
      cross.className = 'btn-close btn-close-white btn-sm ms-1 delete-tag-btn';
      cross.setAttribute('data-tag', tag);
      cross.addEventListener('click', function (e) {
        e.stopPropagation();
        deleteTag(tag);
      });
      pill.appendChild(cross);

      pill.addEventListener('click', function () {
        window.location.href = '/?tag=' + encodeURIComponent(tag);
      });
      modalTags.appendChild(pill);
    });
  } else {
    modalTags.innerHTML = '<em>No tags yet</em>';
  }
}

var imageModal = document.getElementById('imageModal');
imageModal.addEventListener('show.bs.modal', function (event) {
  var trigger = event.relatedTarget;
  // Set the current index based on the clicked element.
  currentIndex = galleryImages.indexOf(trigger);
  updateModalFromElement(trigger);
});


var modalKeydownHandler = function (event) {
  if (!document.querySelector('.modal.show')) return;

  if (event.key === "ArrowLeft") {
    currentIndex = (currentIndex - 1 + galleryImages.length) % galleryImages.length;
    updateModalFromElement(galleryImages[currentIndex]);
  } else if (event.key === "ArrowRight") {
    currentIndex = (currentIndex + 1) % galleryImages.length;
    updateModalFromElement(galleryImages[currentIndex]);
  }
};

imageModal.addEventListener('shown.bs.modal', function () {
  document.addEventListener('keydown', modalKeydownHandler);
});

imageModal.addEventListener('hidden.bs.modal', function () {
  document.removeEventListener('keydown', modalKeydownHandler);
});

document.addEventListener('click', function (e) {
  if (e.target && e.target.classList.contains('copy-text')) {
    var textToCopy = e.target.textContent;
    navigator.clipboard.writeText(textToCopy).then(function () {
      alert('Prompt copied to clipboard!');
    }).catch(function (err) {
      alert('Failed to copy text.');
    });
  }
});

document.getElementById('addTagButton').addEventListener('click', function () {
  var newTagInput = document.getElementById('newTagInput');
  var newTag = newTagInput.value.trim();
  if (newTag === '') return;

  var imageFile = document.getElementById('modalImage').getAttribute('data-imagefile');
  var formData = new FormData();
  formData.append('image_file', imageFile);
  formData.append('tag', newTag);

  fetch('/add_tag', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        var modalTags = document.getElementById('modalTags');
        if (modalTags.innerHTML.includes('No tags yet')) {
          modalTags.innerHTML = '';
        }
        var pill = document.createElement('span');
        pill.className = 'badge rounded-pill bg-primary me-1 tag-pill';
        pill.style.cursor = 'pointer';
        pill.setAttribute('data-tag', data.tag);
        pill.textContent = data.tag;

        var cross = document.createElement('button');
        cross.className = 'btn-close btn-close-white btn-sm ms-1 delete-tag-btn';
        cross.setAttribute('data-tag', data.tag);
        cross.addEventListener('click', function (e) {
          e.stopPropagation();
          deleteTag(data.tag);
        });
        pill.appendChild(cross);

        pill.addEventListener('click', function () {
          window.location.href = '/?tag=' + encodeURIComponent(data.tag);
        });
        modalTags.appendChild(pill);
        newTagInput.value = '';
      } else {
        alert('Error: ' + data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error adding tag');
    });
});

function deleteTag(tag) {
  var imageFile = document.getElementById('modalImage').getAttribute('data-imagefile');
  var formData = new FormData();
  formData.append('image_file', imageFile);
  formData.append('tag', tag);

  fetch('/delete_tag', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        var modalTags = document.getElementById('modalTags');
        var pills = modalTags.getElementsByClassName('tag-pill');
        for (var i = pills.length - 1; i >= 0; i--) {
          if (pills[i].getAttribute('data-tag') === tag) {
            pills[i].remove();
          }
        }
        if (modalTags.children.length === 0) {
          modalTags.innerHTML = '<em>No tags yet</em>';
        }
      } else {
        alert('Error: ' + data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error deleting tag');
    });
}

// random pill colors
document.addEventListener('DOMContentLoaded', function () {
  var tagPills = document.querySelectorAll('.tag-pill');
  var colors = [
    'rgb(252, 204, 0)', 
    'rgb(173, 221, 255)',
    'rgb(143, 154, 255)',
    'rgb(255, 189, 249)',
    'rgb(255, 223, 186)',
    'rgb(186, 255, 201)',
    'rgb(255, 186, 186)',
    'rgb(186, 199, 255)', 
  ];

  tagPills.forEach(tag => {
    var randomColor = colors[Math.floor(Math.random() * colors.length)];
    tag.style.backgroundColor = randomColor;
  });
});
