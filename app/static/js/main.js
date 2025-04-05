document.addEventListener("DOMContentLoaded", function () {
  // Get DOM elements
  const uploadForm = document.getElementById("upload-form");
  const videoFile = document.getElementById("video-file");
  const uploadBtn = document.getElementById("upload-btn");
  const uploadProgress = document.getElementById("upload-progress");
  const progressBar = uploadProgress.querySelector(".progress-bar");
  const segmentsList = document.getElementById("segments-list");
  const uploadStatus = document.getElementById("upload-status");

  // Check if all required elements exist
  if (
    !uploadForm ||
    !videoFile ||
    !uploadBtn ||
    !uploadProgress ||
    !segmentsList ||
    !uploadStatus
  ) {
    console.error("Required DOM elements not found");
    return;
  }

  // Format time in MM:SS format
  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes
      .toString()
      .padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
  }

  // Format file size
  function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  // Create a segment item element
  function createSegmentItem(segment) {
    const segmentItem = document.createElement("div");
    segmentItem.className = "segment-item";

    // Create time range element
    const timeRange = document.createElement("div");
    timeRange.className = "segment-time";
    timeRange.innerHTML = `
      <i class="far fa-clock"></i>
      <span>${formatTime(segment.start)} → ${formatTime(segment.end)}</span>
    `;

    // Create preview frames container if frames are available
    if (segment.preview_frames && segment.preview_frames.length > 0) {
      const framesContainer = document.createElement("div");
      framesContainer.className = "preview-frames";

      segment.preview_frames.forEach((framePath) => {
        const frameImg = document.createElement("img");
        frameImg.src = framePath;
        frameImg.alt = "Segment preview";
        frameImg.className = "preview-frame";
        framesContainer.appendChild(frameImg);
      });

      segmentItem.appendChild(framesContainer);
    }

    // Create labels element
    const labelsContainer = document.createElement("div");
    labelsContainer.className = "segment-labels";

    if (segment.labels && segment.labels.length > 0) {
      segment.labels.forEach((label) => {
        const labelBadge = document.createElement("span");
        labelBadge.className = "label-badge";
        labelBadge.innerHTML = `<i class="fas fa-tag"></i>${label}`;
        labelsContainer.appendChild(labelBadge);
      });
    } else {
      const noLabels = document.createElement("span");
      noLabels.className = "text-muted";
      noLabels.textContent = "No labels available";
      labelsContainer.appendChild(noLabels);
    }

    // Create ads container
    const adsContainer = document.createElement("div");
    adsContainer.className = "segment-ads";

    // Add ads title
    const adsTitle = document.createElement("h6");
    adsTitle.innerHTML = "<i class='fas fa-ad'></i>Suggested Ads";
    adsContainer.appendChild(adsTitle);

    // Add ads list
    const adsList = document.createElement("div");
    adsList.className = "row g-4";

    if (segment.ads && segment.ads.length > 0) {
      segment.ads.forEach((ad) => {
        const adCol = document.createElement("div");
        adCol.className = "col-md-4";

        const adCard = document.createElement("div");
        adCard.className = "ad-card";

        // Create card content
        let cardContent = "";

        // Add image if available
        if (ad.image_url) {
          cardContent += `
            <img src="${ad.image_url}" alt="${ad.title}" class="card-img-top" 
              onerror="this.onerror=null; this.src='https://via.placeholder.com/300x200?text=Ad+Preview';">
          `;
        }

        cardContent += `
          <div class="card-body">
            <h5 class="card-title">${ad.title}</h5>
            <p class="card-text">${ad.description}</p>
        `;

        // Add "Go to Ad" button if URL is available
        if (ad.video_url || ad.url) {
          const adUrl = ad.video_url || ad.url;
          cardContent += `
            <a href="${adUrl}" class="btn btn-primary" target="_blank" rel="noopener noreferrer">
              <i class="fas fa-external-link-alt"></i>
              <span>Go to Ad</span>
            </a>
          `;
        }

        cardContent += "</div>";
        adCard.innerHTML = cardContent;

        // Make entire card clickable if there's a URL
        if (ad.video_url || ad.url) {
          const adUrl = ad.video_url || ad.url;
          adCard.style.cursor = "pointer";
          adCard.addEventListener("click", (e) => {
            // Don't trigger if clicking on the button
            if (!e.target.closest(".btn")) {
              window.open(adUrl, "_blank", "noopener noreferrer");
            }
          });
        }

        adCol.appendChild(adCard);
        adsList.appendChild(adCol);
      });
    } else {
      const noAds = document.createElement("div");
      noAds.className = "col-12";
      noAds.innerHTML =
        "<p class='text-muted text-center'>No ads available for this segment</p>";
      adsList.appendChild(noAds);
    }

    adsContainer.appendChild(adsList);

    // Add all elements to segment item
    segmentItem.appendChild(timeRange);
    segmentItem.appendChild(labelsContainer);
    segmentItem.appendChild(adsContainer);

    // Add click event to seek to segment start
    timeRange.addEventListener("click", () => {
      videoPlayer.currentTime = segment.start;
      videoPlayer.play().catch((e) => console.error("Error playing video:", e));

      // Highlight active segment
      document.querySelectorAll(".segment-item").forEach((item) => {
        item.classList.remove("active");
      });
      segmentItem.classList.add("active");

      // Scroll segment into view
      segmentItem.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });

    return segmentItem;
  }

  // Handle form submission
  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent form from submitting normally

    if (!videoFile.files.length) {
      alert("Please select a video file");
      return;
    }

    const file = videoFile.files[0];
    const formData = new FormData();
    formData.append("video", file);

    // Update UI for upload start
    uploadProgress.style.display = "block";
    progressBar.style.width = "0%";
    uploadStatus.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <i class="fas fa-upload"></i>
        <span>Uploading ${file.name} (${formatFileSize(file.size)})</span>
      </div>
    `;
    uploadBtn.disabled = true;
    uploadBtn.innerHTML =
      "<i class='fas fa-spinner fa-spin'></i> Processing...";

    // Use XMLHttpRequest for upload progress
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", function (e) {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        progressBar.style.width = percentComplete + "%";
        progressBar.setAttribute("aria-valuenow", percentComplete);
      }
    });

    xhr.onload = function () {
      if (xhr.status === 200) {
        try {
          const data = JSON.parse(xhr.responseText);
          if (data.success) {
            // Display segments
            segmentsList.innerHTML = "";
            data.segments.forEach((segment) => {
              segmentsList.appendChild(createSegmentItem(segment));
            });

            // Update status
            uploadStatus.innerHTML = `
              <div class="d-flex align-items-center gap-2 text-success">
                <i class="fas fa-check-circle"></i>
                <span>Upload complete! Video processed successfully.</span>
              </div>
            `;
          } else {
            throw new Error(data.error || "Upload failed");
          }
        } catch (error) {
          console.error("Error parsing response:", error);
          uploadStatus.innerHTML = `
            <div class="d-flex align-items-center gap-2 text-danger">
              <i class="fas fa-exclamation-circle"></i>
              <span>Error: ${error.message}</span>
            </div>
          `;
        }
      } else {
        uploadStatus.innerHTML = `
          <div class="d-flex align-items-center gap-2 text-danger">
            <i class="fas fa-exclamation-circle"></i>
            <span>Error: Upload failed (${xhr.status})</span>
          </div>
        `;
      }
    };

    xhr.onerror = function () {
      console.error("Network Error:", xhr.statusText);
      uploadStatus.innerHTML = `
        <div class="d-flex align-items-center gap-2 text-danger">
          <i class="fas fa-exclamation-circle"></i>
          <span>Network Error: Could not connect to server</span>
        </div>
      `;
    };

    xhr.onloadend = function () {
      // Reset UI
      uploadProgress.style.display = "none";
      uploadBtn.disabled = false;
      uploadBtn.innerHTML = "<i class='fas fa-upload'></i> Upload & Process";
    };

    // Send the request
    xhr.open("POST", "/upload", true);
    xhr.send(formData);
  });

  // Update UI when file is selected
  videoFile.addEventListener("change", function () {
    if (this.files.length > 0) {
      const file = this.files[0];
      uploadStatus.innerHTML = `
        <div class="d-flex align-items-center gap-2 text-muted">
          <i class="fas fa-file-video"></i>
          <span>Selected: ${file.name} (${formatFileSize(file.size)})</span>
        </div>
      `;

      // Reset progress bar
      progressBar.style.width = "0%";
      progressBar.setAttribute("aria-valuenow", 0);
    }
  });
});
