document.getElementById("live-btn").addEventListener("click", function() {
    document.getElementById("video-feed").src = "/live_detect";
    document.getElementById("video-feed").style.display = "block";
});

document.getElementById("stop-btn").addEventListener("click", function() {
    document.getElementById("video-feed").src = "";
    document.getElementById("video-feed").style.display = "none";
});
