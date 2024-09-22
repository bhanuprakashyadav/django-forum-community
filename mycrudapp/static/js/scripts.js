function create_post() {
  document
    .querySelector(".create-post-button")
    .addEventListener("click", function (event) {
      event.preventDefault();

      fetch("/check_login", {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.authenticated) {
            window.location.href = "/create_post";
          } else {
            openLoginModal();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
}

function replyToPost() {
  const form = document.querySelector(".reply-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const replyText = this.querySelector('textarea[name="replyarea"]').value;

      const csrfToken = this.querySelector(
        'input[name="csrfmiddlewaretoken"]'
      ).value;
      const postId = this.getAttribute("data-post-id");
      const replyId = this.getAttribute("data-reply-id");

      console.log(
        "Submitting reply:",
        replyText,
        "Post ID:",
        postId,
        " Reply Id:",
        replyId
      );

      fetch("/post_reply/", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },

        body: JSON.stringify({
          post_id: postId,
          replyarea: replyText,
          reply_id: replyId,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Response data:", data);
          if (data.success) {
            const newReply = document.createElement("div");
            newReply.className = "reply";
            newReply.innerHTML = `
                        <p>${data.reply_text}</p>
                        <small>Replied by: <b>${data.user}</b> at <b>${data.created_at}</b></small>
                        <hr>
                    `;
            const repliesContainer = document.getElementById(
              `replies-container-${postId}`
            );
            repliesContainer.insertBefore(
              newReply,
              repliesContainer.lastElementChild
            );
            console.log("Last child is ", repliesContainer.lastChild);
            console.log(
              "Last element child is ",
              repliesContainer.lastElementChild
            );

            this.querySelector('textarea[name="replyarea"]').value = "";
          } else {
            throw new Error(data.message);
          }
        })
        .catch((error) => {
          console.log("Error is " + error);
        });
    });
  }
}

document.addEventListener("DOMContentLoaded", replyToPost);

function scrollToReply() {
  var textarea = document.getElementById("reply_text");
  if (textarea) {
    textarea.scrollIntoView({ behavior: "smooth" });
    textarea.focus();
  } else {
    window.scrollTo({
      left: 0,
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie != "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();

      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function delete_reply(replyId, postId) {
  console.log("Deleting reply with ID:", replyId, "for post:", postId);

  fetch(`/post/${postId}/reply/${replyId}/delete/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log(
        `Current User is ${data.current_usr} Replied by ${data.reply_user}`
      );

      if (data.success) {
        const replyElement = document.querySelector(
          `[data-reply-id="${replyId}"]`
        );
        if (replyElement) {
          replyElement.remove();
          console.log("Reply Element Removed");
        }
      } else {
        console.log("Error:", data.message);
      }
    })
    .catch((error) => {
      console.log("Error is :", error);
    });
}

async function report_post() {
  const isUserLoggedIn = await check_auth();
  if (isUserLoggedIn) {
    alert("Reported!");
  } else {
    alert("Log in first");
  }
}

async function check_auth() {
  try {
    const response = await fetch("/check_login/", {
      method: "GET",
    });
    const data = await response.json();
    if (data.authenticated) {
      console.log("Data is true", data.username);
      return true;
    } else {
      console.log("Data is false", data.username);
      return false;
    }
  } catch (error) {
    console.error("Error is:", error);
    return false;
  }
}

function openLoginModal() {
  if (document.getElementById("signUpModal").style.display === "block") {
    document.getElementById("signUpModal").style.display = "none";
  }
  document.getElementById("loginModal").style.display = "block";
}

function openSignUpModal() {
  if (document.getElementById("loginModal").style.display === "block") {
    document.getElementById("loginModal").style.display = "none";
  }
  document.getElementById("signUpModal").style.display = "block";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

window.onclick = function (event) {
  var loginModal = document.getElementById("loginModal");
  var signUpModal = document.getElementById("signUpModal");
  if (event.target == loginModal) {
    loginModal.style.display = "none";
  }
  if (event.target == signUpModal) {
    signUpModal.style.display = "none";
  }
};

document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("upload-button")
    .addEventListener("click", function () {
      document.getElementById("file-input").click();
    });

  document
    .getElementById("file-input")
    .addEventListener("change", function (event) {
      const fileInput = event.target;
      console.log("element is " + event.target);
      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const reader = new FileReader();

        reader.onload = function (e) {
          document.getElementById("profile_pic").src = e.target.result;
          console.log("src is " + e.target.result);
          console.log("file is " + file);
        };
        reader.readAsDataURL(file);
      }
    });
});

function showDropdown(event) {
  event.stopPropagation();
  const dropdownContent = event.currentTarget.nextElementSibling;
  dropdownContent.style.display =
    dropdownContent.style.display === "block" ? "none" : "block";
}

window.onclick = function (event) {
  if (!event.target.matches(".dropdownbtn, .dropdownbtn *")) {
    var dropdowns = document.getElementsByClassName("dropdownPost-content");
    for (var i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.style.display === "block") {
        openDropdown.style.display = "none";
      }
    }
  }
};

function formatText(command) {
  document.execCommand(command);
}

document.querySelectorAll(".star-button").forEach((button) => {
  button.addEventListener("click", function () {
    this.classList.toggle("active");
  });
});

function toggleDropdown() {
  var dropdownMenu = document.getElementById("dropdown-menu");
  dropdownMenu.style.display =
    dropdownMenu.style.display === "block" ? "none" : "block";
}

document.addEventListener("click", function (event) {
  var dropdownMenu = document.getElementById("dropdown-menu");
  var profileButton = document.querySelector(".profile-button");
  if (
    !profileButton.contains(event.target) &&
    !dropdownMenu.contains(event.target)
  ) {
    dropdownMenu.style.display = "none";
  }
});

var themeToggle = document.getElementById("theme-toggle");

if (window.localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode");
  themeToggle.textContent = "☀️";
} else {
  document.body.classList.add("light-mode");
  themeToggle.textContent = "🌙";
}

themeToggle.addEventListener("click", function () {
  if (document.body.classList.contains("dark-mode")) {
    document.body.classList.remove("dark-mode");
    document.body.classList.add("light-mode");
    localStorage.setItem("theme", "light");
    themeToggle.textContent = "🌙";
  } else {
    document.body.classList.remove("light-mode");
    document.body.classList.add("dark-mode");
    localStorage.setItem("theme", "dark");
    themeToggle.textContent = "☀️";
  }
});
