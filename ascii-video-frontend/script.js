const form = document.getElementById("uploadForm");
const videoInput = document.getElementById("videoInput");
const widthInput = document.getElementById("widthInput");
const brightnessInput = document.getElementById("brightnessInput");
const statusBox = document.getElementById("status");

// ✅ Replace this with your Render API URL
const API_URL = "https://ascii-video-api.onrender.com/convert";

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = videoInput.files[0];
  if (!file) {
    alert("Please choose a video file.");
    return;
  }

  const formData = new FormData();
  formData.append("video", file);
  formData.append("width", widthInput.value);
  formData.append("brightness", brightnessInput.value);

  statusBox.innerText = "⏳ Converting... please wait.";

  try {
    const response = await fetch(API_URL, { method: "POST", body: formData });
    if (!response.ok) throw new Error("Conversion failed.");

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ascii_video.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();

    statusBox.innerText = "✅ Done! Downloading ASCII video...";
  } catch (error) {
    statusBox.innerText = "❌ Error: " + error.message;
  }
});
