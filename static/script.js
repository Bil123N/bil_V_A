function toggleAssistant() {
    var button = document.getElementById('activate-btn');
    var buttonText = button.innerText;

    // // Add hover effect with uppercase text transformation
    // button.addEventListener('mouseenter', function() {
    //     button.style.textTransform = 'uppercase';
    // });

    // button.addEventListener('mouseleave', function() {
    //     button.style.textTransform = 'none'; // Revert to original text transformation on mouse leave
    // });


    if (buttonText === 'Activate Assistant') {
        button.innerText = 'Deactivate Assistant';
        button.disabled = true;

        fetch('/activate_assistant', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.response);
                alert(data.response); // Display response in an alert
                button.disabled = false;
                logoImg = document.getElementById('robotImg')
                logoImg.src = "static/img/chatbot_2.png";
                document.getElementById('robotStatus').innerText = "On";
                logoImg.classList.remove('inactive');
                logoImg.classList.remove('active2');
                logoImg.classList.add('active');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
                button.disabled = false;
            });
    } else {
        button.innerText = 'Activate Assistant';
        button.disabled = true;

        fetch('/deactivate_assistant', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.response);
                alert(data.response); // Display response in an alert
                button.disabled = false;
                logoImg = document.getElementById('robotImg')
                logoImg.src =  "static/img/chatbot_4.png";
                document.getElementById('robotStatus').innerText = "Off";
                logoImg.classList.remove('active');
                logoImg.classList.remove('active2');
                logoImg.classList.add('inactive');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
                button.disabled = false;
            });
    }
}

let assistantActive = false; // Flag to track the activation state

function fetchOutput() {
    fetch('/get_output')
    .then(response => response.text())
    .then(data => {
        document.getElementById('output').innerHTML = data;

        // Check if "You said: activate" is present in the output
        const activateIndex = data.lastIndexOf("Assistance is Activated.");
        // Check if "You said: deactivate" is present in the output
        const deactivateIndex = data.lastIndexOf("The assistance is deactivated.");

        // Update the UI based on the presence of activation or deactivation commands
        if (activateIndex > deactivateIndex) {
            // If the last activate command occurred after the last deactivate command
            assistantActive = true;
            document.getElementById('Result').innerText = "Welcome, I'm activated";
            document.getElementById('Result2').innerText = "";
            logoImg = document.getElementById('robotImg')
            logoImg.src =  "static/img/chatbot_3.png";
            logoImg.classList.remove('inactive');
            logoImg.classList.remove('active');
            logoImg.classList.add('active2');
        } else if (deactivateIndex > activateIndex) {
            // If the last deactivate command occurred after the last activate command
            assistantActive = false;
            document.getElementById('Result').innerText = "";
            document.getElementById('Result2').innerText = "Waiting for activation word!";
            document.getElementById('robotImg').src = "static/img/chatbot_2.png";
            logoImg = document.getElementById('robotImg')
            logoImg.src =  "static/img/chatbot_2.png";
            logoImg.classList.remove('inactive');
            logoImg.classList.remove('active2');
            logoImg.classList.add('active');
        } else {
            // If neither activation nor deactivation command is present
            document.getElementById('Result').innerText = "";
        }
    })
    .catch(error => console.error('Error:', error));
}

// Fetch output every second
setInterval(fetchOutput, 1000);


function clearOutput() {
    document.getElementById('output').innerHTML = "";
    fetch('/clear_output', { method: 'POST' }) // Clear the captured output on the server side
        .then(response => response.json())
        .then(data => console.log(data.message))
        .catch(error => console.error('Error:', error));
}


// additional


function toggleContent(event) {
    const targetId = event.currentTarget.dataset.target;
    const targetElement = document.querySelector(`#${targetId}`);
    const containerElement = document.querySelector(`#checkboxContainer${targetId}`);
  
    if (targetElement.style.display === "none") {
      targetElement.style.display = "block";
      containerElement.style.display = "block";
    } else {
      targetElement.style.display = "none";
      containerElement.style.display = "none";
    }
  }
  
  const toggleLabels = document.querySelectorAll(".toggle-label");
  toggleLabels.forEach((toggleLabel) => {
    toggleLabel.addEventListener("click", toggleContent);
  });



  /// the change
  $(document).ready(function () {
    // Initialize VanillaTilt with default values
    var cards = document.querySelectorAll(".card");
    cards.forEach(function (card) {
      VanillaTilt.init(card, {
        max: 25,
        speed: 400,
        glare: true,
        "max-glare": 0.5,
      });
    });
  
    $(".topImg2").click(function () {
      var contentDiv = $(this).closest(".card").find(".content");
      $(".topImg2").not(this).show(); // Show all other images except the clicked one
      $(this).hide(); // Hide the clicked image
      $(".content").hide(); // Hide all content elements
      contentDiv.show(); // Show the content associated with the clicked image
  
      // Enable or disable the functionality of VanillaTilt based on image visibility
      cards.forEach(function (card) {
        if ($(card).find(".topImg2").is(":visible")) {
          VanillaTilt.init(card, {
            max: 25,
            speed: 400,
            glare: true,
            "max-glare": 0.5,
          }); // Enable the functionality of VanillaTilt
        } else {
          card.vanillaTilt.destroy(); // Disable the functionality of VanillaTilt
        }
      });
    });
  });
// Function to hide content when clicking outside containers
function hideContentOnClickOutside(event) {
    const containers = document.querySelectorAll('.containerHide');
    let clickedOutside = true;

    // Check if the click event occurred inside any of the .container elements
    containers.forEach(container => {
        if (container.contains(event.target)) {
            clickedOutside = false;
        }
    });

    // Hide the .content elements if the click occurred outside the .container elements
    if (clickedOutside) {
        logoImg = document.querySelector('.topImg2')
        document.querySelectorAll('.content').forEach(content => {
            content.style.display = 'none';
            logoImg.style.display = 'block';
        });
    }
}

// Attach event listener to the window object to capture all clicks
window.addEventListener('click', hideContentOnClickOutside);
