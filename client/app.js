(function () {
  // LiveKit client SDK exports as LivekitClient (or livekitClient in some builds)
  var LIVEKIT = window.LivekitClient || window.livekitClient;
  if (!LIVEKIT) {
    console.error("LiveKit client SDK not loaded. Check script: livekit-client.umd.min.js");
    document.getElementById("status").textContent = "Error: LiveKit SDK not loaded";
    return;
  }

  var Room = LIVEKIT.Room;
  var RoomEvent = LIVEKIT.RoomEvent || (Room && Room.Event);
  var Track = LIVEKIT.Track;
  var TrackKind = (Track && Track.Kind) || {};
  if (!RoomEvent) {
    console.error("LiveKit RoomEvent not found");
    return;
  }
  var room = null;
  var remoteAudioContainer = document.getElementById("remote-audio-container");
  var agentAudioEl = document.getElementById("agent-audio");
  var btnStartAudio = document.getElementById("btn-start-audio");

  var statusEl = document.getElementById("status");
  var btnStart = document.getElementById("btn-start");
  var btnEnd = document.getElementById("btn-end");

  function setStatus(text, className) {
    statusEl.textContent = text;
    statusEl.className = "status " + (className || "ready");
  }

  function setConnecting() {
    setStatus("Connecting…", "connecting");
    btnStart.disabled = true;
  }

  function setConnected() {
    setStatus("In call", "connected");
    btnEnd.hidden = false;
  }

  function setEnded() {
    setStatus("Call ended", "ready");
    btnStart.disabled = false;
    btnEnd.hidden = true;
  }

  function setError(msg) {
    setStatus("Error: " + msg, "error");
    btnStart.disabled = false;
    btnEnd.hidden = true;
  }

  function getTokenServer() {
    return window.location.origin + "/start-call";
  }

  function removeEl(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function setStartAudioButton(show) {
    if (btnStartAudio) btnStartAudio.style.display = show ? "inline-block" : "none";
  }

  function playAgentAudio() {
    if (agentAudioEl && typeof agentAudioEl.play === "function") {
      agentAudioEl.play().catch(function () {});
    }
  }

  async function startCall() {
    setConnecting();
    try {
      var tokenUrl = getTokenServer();
      console.log("Fetching token from", tokenUrl);
      var res = await fetch(tokenUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        var errText = await res.text();
        throw new Error(res.status + " " + errText);
      }
      var data = await res.json();
      var url = data.url;
      var token = data.token;
      if (!url || !token) {
        throw new Error("Invalid response: missing url or token");
      }
      console.log("Got token, connecting to", url);

      room = new Room();
      room.on(RoomEvent.Disconnected, function (reason) {
        console.log("Disconnected:", reason);
        onDisconnected();
      });
      room.on(RoomEvent.MediaDevicesError, function (err) {
        console.error("MediaDevicesError", err);
        setError(err && err.message ? err.message : "Microphone access denied or unavailable");
      });
      room.on(RoomEvent.Connected, function () {
        console.log("Connected to room");
      });
      room.on(RoomEvent.TrackSubscribed, function (track, publication, participant) {
        var isAudio = track.kind === "audio" || track.kind === TrackKind.Audio;
        if (!isAudio || !agentAudioEl) return;
        var localIdentity = room.localParticipant && room.localParticipant.identity;
        if (participant && participant.identity === localIdentity) return;
        try {
          track.attach(agentAudioEl);
          console.log("Remote audio attached (participant: " + (participant ? participant.identity : "?") + ")");
          playAgentAudio();
          if (room && !room.canPlaybackAudio) setStartAudioButton(true);
        } catch (err) {
          console.error("Attach agent audio failed", err);
        }
      });
      room.on(RoomEvent.TrackUnsubscribed, function (track) {
        track.detach();
        if (agentAudioEl) {
          agentAudioEl.srcObject = null;
          agentAudioEl.src = "";
        }
      });
      room.on(RoomEvent.AudioPlaybackStatusChanged, function () {
        if (room && room.canPlaybackAudio) {
          setStartAudioButton(false);
          playAgentAudio();
        } else {
          setStartAudioButton(true);
        }
      });

      if (typeof room.prepareConnection === "function") {
        await room.prepareConnection(url, token);
      }
      await room.connect(url, token);
      if (typeof room.startAudio === "function") {
        try {
          await room.startAudio();
          setStartAudioButton(false);
          playAgentAudio();
        } catch (audioErr) {
          console.warn("startAudio:", audioErr);
          setStartAudioButton(true);
        }
      }
      try {
        await room.localParticipant.setMicrophoneEnabled(true);
      } catch (micErr) {
        console.warn("Microphone enable failed (continuing without mic):", micErr);
      }
      setConnected();
      setStartAudioButton(true);
      if (room && typeof room.canPlaybackAudio !== "undefined" && room.canPlaybackAudio) {
        setStartAudioButton(false);
      }
    } catch (e) {
      console.error("startCall error", e);
      setError(e.message || "Connection failed");
      if (room) {
        try { room.disconnect(); } catch (_) {}
        room = null;
      }
    }
  }

  function onDisconnected() {
    if (agentAudioEl) {
      agentAudioEl.srcObject = null;
      agentAudioEl.src = "";
    }
    setStartAudioButton(false);
    room = null;
    setEnded();
  }

  function endCall() {
    if (room) {
      room.disconnect();
    }
  }

  if (btnStartAudio) {
    btnStartAudio.addEventListener("click", function () {
      if (!room || typeof room.startAudio !== "function") return;
      room.startAudio().then(function () {
        setStartAudioButton(false);
        playAgentAudio();
      }).catch(function (e) { console.warn("startAudio:", e); });
    });
  }
  btnStart.addEventListener("click", startCall);
  btnEnd.addEventListener("click", endCall);
})();
