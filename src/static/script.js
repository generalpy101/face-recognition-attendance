const video = document.getElementById("video");
const main = document.getElementsByClassName("l");
const messageBox = document.querySelector(".message");
const page = document.querySelector(".capture-page");

let imgBase64;

let flag = true;
Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri("static/models"),
  // faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
  // faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
  // faceapi.nets.faceExpressionNet.loadFromUri('/models')
]).then(startVideo);

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    (stream) => (video.srcObject = stream),
    (err) => console.error(err)
  );
}

let sendRequest = () => {
  data = {
    images: imgBase64,
  };
  fetch("/identify-face", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then((res) => {
    if (res.status == 401) {
      messageBox.innerHTML = `
      <div class="message-danger">
        No user found, please <a href="/register">register</a> user if not done already
      </div>`;
      return;
    }
    if (res.status == 409) {
      messageBox.innerHTML = `
      <div class="message-danger">Your attendace has been already recorded for today, come back later
      </div>`;
      return;
    }
    console.log(res);
    if (res.redirected) {
      window.location.href = res.url;
    }
  });
};

video.addEventListener("play", () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  page.append(canvas);
  const displaySize = { width: video.width, height: video.height };
  faceapi.matchDimensions(canvas, displaySize);
  setInterval(async () => {
    const detections = await faceapi.detectAllFaces(
      video,
      new faceapi.TinyFaceDetectorOptions({ inputSize: 128 })
    );
    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    faceapi.draw.drawDetections(canvas, resizedDetections);

    if (resizedDetections.length > 0 && resizedDetections[0]._score > 0.5) {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.ma;
      canvas.getContext("2d").drawImage(video, 0, 0);
      if (flag == false) return;
      const img = document.createElement("img");
      img.src = canvas.toDataURL("image/png");
      imgBase64 = canvas.toDataURL("image/png");
      console.log(img.src);
      if (flag) sendRequest();
      flag = false;
    }
  }, 100);
});
