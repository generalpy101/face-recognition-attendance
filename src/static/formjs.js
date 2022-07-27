const prevBtns = document.querySelectorAll(".btn-prev");
const nextBtns = document.querySelectorAll(".btn-next");
const progress = document.getElementById("progress");
const formSteps = document.querySelectorAll(".form-step");
const progressSteps = document.querySelectorAll(".progress-step");
const submitBtn = document.querySelector(".btn-submit")
const message = document.querySelector(".message")

/*----- for camera------*/;
let image_data_url;
let camera_button = document.querySelector("#start-camera");
let camera_of_button = document.querySelector("#stop-camera");
let video = document.querySelector("#video");
let click_button = document.querySelector("#click-photo");
let canvas = document.querySelector("#canvas");
let dataurl = document.querySelector("#dataurl");
let dataurl_container = document.querySelector("#dataurl-container");
let formStepsNum = 0;
/--------end-----------/;
let localStream;
let OnEvent;
OnEvent = new CustomEvent("ONN", {});
let OfEvent;
OfEvent = new CustomEvent("OFF", {});

nextBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    formStepsNum++;
    if (formStepsNum == 1) {
      camera_button.dispatchEvent(OnEvent);
    }
    updateFormSteps();
    updateProgressbar();
  });
});

prevBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    formStepsNum--;

    if (formStepsNum != 1) {
      camera_of_button.dispatchEvent(OfEvent);
    }
    updateFormSteps();
    updateProgressbar();
  });
});

function updateFormSteps() {
  formSteps.forEach((formStep) => {
    formStep.classList.contains("form-step-active") &&
      formStep.classList.remove("form-step-active");
  });

  formSteps[formStepsNum].classList.add("form-step-active");
}

function updateProgressbar() {
  progressSteps.forEach((progressStep, idx) => {
    if (idx < formStepsNum + 1) {
      progressStep.classList.add("progress-step-active");
    } else {
      progressStep.classList.remove("progress-step-active");
    }
  });

  const progressActive = document.querySelectorAll(".progress-step-active");

  progress.style.width =
    ((progressActive.length - 1) / (progressSteps.length - 1)) * 100 + "%";
}

camera_button.addEventListener("ONN", async function () {
  let stream = null;

  try {
    localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false,
    });
  } catch (error) {
    alert(error.message);
    return;
  }

  video.srcObject = localStream;

  video.style.display = "block";
  camera_button.style.display = "none";
  click_button.style.display = "block";
});

camera_of_button.addEventListener("OFF", async function () {
  localStream.getVideoTracks()[0].stop();
  video.src = "";
});

click_button.addEventListener("click", function () {
  submitBtn.classList.remove("hidden")
  canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
   image_data_url = canvas.toDataURL("application/octet-stream");
  console.log(image_data_url);
});

submitBtn.addEventListener("click",(e) => {
  e.preventDefault()
    let jsonToSend = {
      "name" : document.getElementById("username").value,
      "regid" : document.getElementById("position").value,
      "rollno" : document.getElementById("rollnumber").value,
      "branch" : document.getElementById("branch").value,
      "year" : document.getElementById("year").value,
      "password" : document.getElementById("password").value,
      "images" : image_data_url
    }
    fetch("register-student",{
      method : "POST",
      headers : {
        "Content-Type" : "application/json"
      },
      body : JSON.stringify(jsonToSend)
    }).then(res => {
      
      if(res.status == 404) {
        console.log(res)
        message.innerHTML = `
        <div class="message-danger">Error multiple/no face(s) detected</div>
      `
      }

      if (res.status == 409) {
        message.innerHTML = `
          <div class="message-danger">User face is already registered, contact admin to delete it.</div>
        `
      }
      if(res.redirected) {
        location.href = res.url
      }
    })//.then(dat => console.log(dat))
})