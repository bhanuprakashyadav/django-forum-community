function create_post() {
    document.querySelector('.create-post-button').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default form submission
        
        fetch('/check_login', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // Make it an AJAX request
            }
        })
        .then(response => response.json()) // Resolve the promise
        .then(data => { // If we got data
            if (data.authenticated) {
                window.location.href = '/create_post'; // Redirect to create_post page
            } else {
                openLoginModal(); // Open the login modal
            }
        })
        .catch(error => {
            console.error('Error:', error); // Handle any errors
        });
    });
}

function replyToPost() { //sent to server that is views.py
    const form = document.querySelector('.reply-form');
    if(form){
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const replyText = this.querySelector('textarea[name="replyarea"]').value;

            //Gets the CSRF token, which is REQUIRED by Django to validate POST requests.
            const csrfToken = this.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const postId = this.getAttribute('data-post-id');

            console.log('Submitting reply:', replyText, 'Post ID:', postId);

            fetch('/post_reply/', {  //A POST request is sent to the /post_reply/ endpoint using the fetch API.
                method: 'POST',

                /*
                Request headers give the server information about the request:
                 for example, the Content-Type header tells the server the format of the request's body.
                  Many headers are set automatically by the browser and can't be set by a script:
                   these are called Forbidden header names.
                */
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },

                /* 
                    The request body is the payload of the request: it's the thing the
                     client is sending to the server. You cannot include a body with GET requests,
                      but it's useful for requests that send content to the server,
                       such as POST or PUT requests. For example, 
                       if you want to upload a file to the server, you might make a POST request
                        and include the file as the request body.
                        To set a request body, pass it as the body option:
                
                */
                body: JSON.stringify({ post_id: postId, replyarea: replyText })
            })
            .then(response => response.json()) //if PROMISE resolved
            .then(data => { //data sent from server
                console.log('Response data:', data);
                if (data.success) {
                    const newReply = document.createElement('div');
                    newReply.className = 'reply';
                    newReply.innerHTML = `
                        <p>${data.reply_text}</p>
                        <small>Replied by: <b>${data.user}</b> at <b>${data.created_at}</b></small>
                        <hr>
                    `;
                    const repliesContainer = document.getElementById(`replies-container-${postId}`);
                    repliesContainer.insertBefore(newReply, repliesContainer.lastElementChild);
                    console.log("Last child is ", repliesContainer.lastChild)
                    console.log("Last element child is ", repliesContainer.lastElementChild)
                    //repliesContainer.appendChild(newReply);
                    this.querySelector('textarea[name="replyarea"]').value = '';  
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(error => {
            console.log("Error is " + error);
            });
        });
    }
    
}

//The function replyToPost is executed when the DOM content is fully loaded 
document.addEventListener('DOMContentLoaded', replyToPost);

function scrollToReply()
{
    var textarea = document.getElementById('reply_text');
    textarea.scrollIntoView({behavior: 'smooth'});
    textarea.focus();
}


function openLoginModal() {

    //Check if signup modal is opened if so close it
    if(document.getElementById('signUpModal').style.display === 'block')
    {
        document.getElementById('signUpModal').style.display = 'none';
    }
    document.getElementById('loginModal').style.display = 'block';
}

function openSignUpModal() {
    if(document.getElementById('loginModal').style.display === 'block')
        {
            document.getElementById('loginModal').style.display = 'none';
        }
    document.getElementById('signUpModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

window.onclick = function(event) {
    var loginModal = document.getElementById('loginModal');
    var signUpModal = document.getElementById('signUpModal');
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    }
    if (event.target == signUpModal) {
        signUpModal.style.display = 'none';
    }
}


document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('upload-button').addEventListener('click', function() { //event passed here too, we just dont need
        document.getElementById('file-input').click();
    });

    
    document.getElementById('file-input').addEventListener('change', function(event) {//event passed by browser by default,
        const fileInput = event.target; // = HTMLInputElement , file input element that triggered the change event.
        console.log("element is " + event.target);
        if(fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const reader = new FileReader();
            
            //As the file been read fully, onload, execute the callback function(e)...
            reader.onload = function(e) { //event fired from selecting file
                // convert img to base64
                // image to the Base64-encoded data of the selected file, effectively displaying the chosen image in the browser
                document.getElementById('profile_pic').src = e.target.result; 
                console.log("src is " + e.target.result);
                console.log("file is " + file);
            };
            reader.readAsDataURL(file); //representing the file's data as a base64 encoded string.
        }
    });
});

function showDropdown(event) {
    event.stopPropagation();
    const dropdownContent = event.currentTarget.nextElementSibling;
    dropdownContent.style.display = (dropdownContent.style.display === 'block') ? 'none' : 'block';
}

// Close dropdown if clicking outside
window.onclick = function(event) {
    if (!event.target.matches('.dropdownbtn, .dropdownbtn *')) {
        var dropdowns = document.getElementsByClassName("dropdownPost-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.style.display === 'block') {
                openDropdown.style.display = 'none';
            }
        }
    }
};


function formatText(command) {
    document.execCommand(command);
}

// function Cannot read properties of null (reading 'appendChild')() {
//     var date = new Date();
//     var options = { year: 'numeric', month: 'long', day: 'numeric' };
//     document.getElementById('currentDate').textContent = date.toLocaleDateString('en-US', options);
// }

// displayCurrentDate();

document.querySelectorAll('.star-button').forEach(button => {
    button.addEventListener('click', function() {
        this.classList.toggle('active');
    });
});

function toggleDropdown() {
    var dropdownMenu = document.getElementById('dropdown-menu');
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
}

document.addEventListener('click', function(event) {
    var dropdownMenu = document.getElementById('dropdown-menu');
    var profileButton = document.querySelector('.profile-button');
    if (!profileButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.style.display = 'none';
    }
});

var themeToggle = document.getElementById('theme-toggle');

// Check stored theme preference on page load
if (window.localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    themeToggle.textContent = '☀️';
} else {
    document.body.classList.add('light-mode');
    themeToggle.textContent = '🌙';
}

themeToggle.addEventListener('click', function() {
    if (document.body.classList.contains('dark-mode')) {
        document.body.classList.remove('dark-mode');
        document.body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
        themeToggle.textContent = '🌙';
    } else {
        document.body.classList.remove('light-mode');
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        themeToggle.textContent = '☀️';
    }
});
