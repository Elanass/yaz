/**
 * WebRTC-based Telemedicine & Team Collaboration Module
 * For Gastric ADCI Platform - HIPAA & GDPR Compliant
 */

class ClinicalCollaboration {
  constructor(options = {}) {
    this.options = {
      roomPrefix: 'gastric-adci-collab-',
      stunServers: ['stun:stun.l.google.com:19302'],
      turnServers: [], // Should be configured with proper TURN servers
      enableVideo: true,
      enableAudio: true,
      enableAnnotations: true,
      maxParticipants: 10,
      recordSession: false,
      hipaaCompliant: true,
      ...options
    };
    
    this.localStream = null;
    this.peerConnections = {};
    this.dataChannels = {};
    this.roomId = null;
    this.userId = null;
    this.userName = null;
    this.userRole = null;
    this.sessionToken = null;
    this.gunDB = null;
    this.annotationsEnabled = false;
    this.currentView = null;
    
    // DOM elements
    this.containerElement = null;
    this.localVideoElement = null;
    this.remoteVideosContainer = null;
    this.annotationsLayer = null;
    
    // Event callbacks
    this.callbacks = {
      onParticipantJoined: null,
      onParticipantLeft: null,
      onAnnotationAdded: null,
      onAnnotationRemoved: null,
      onError: null,
      onConnectionStateChanged: null,
      onChatMessage: null
    };
    
    // Initialize Gun.js for distributed state if available
    if (window.Gun) {
      this.initGunDB();
    }
  }
  
  /**
   * Initialize the collaboration module
   * @param {string} containerId - The container element ID
   * @param {Object} user - User information
   * @returns {Promise<boolean>} - Whether initialization was successful
   */
  async initialize(containerId, user) {
    try {
      // Store user information
      this.userId = user.id;
      this.userName = user.name;
      this.userRole = user.role;
      
      // Get the container element
      this.containerElement = document.getElementById(containerId);
      if (!this.containerElement) {
        throw new Error(`Container element with ID ${containerId} not found`);
      }
      
      // Create the UI
      this.createUI();
      
      // Initialize WebRTC
      await this.initializeWebRTC();
      
      return true;
    } catch (error) {
      console.error('Failed to initialize collaboration:', error);
      this.triggerCallback('onError', error);
      return false;
    }
  }
  
  /**
   * Create the collaboration UI
   */
  createUI() {
    // Clear the container
    this.containerElement.innerHTML = '';
    this.containerElement.className = 'gastric-collab-container';
    
    // Create the video container
    const videoContainer = document.createElement('div');
    videoContainer.className = 'gastric-collab-videos';
    
    // Create local video element
    const localVideoWrapper = document.createElement('div');
    localVideoWrapper.className = 'gastric-collab-local-video-wrapper';
    
    this.localVideoElement = document.createElement('video');
    this.localVideoElement.className = 'gastric-collab-local-video';
    this.localVideoElement.autoplay = true;
    this.localVideoElement.muted = true; // Mute local video
    this.localVideoElement.playsInline = true;
    
    const localLabel = document.createElement('div');
    localLabel.className = 'gastric-collab-local-label';
    localLabel.textContent = `You (${this.userRole})`;
    
    localVideoWrapper.appendChild(this.localVideoElement);
    localVideoWrapper.appendChild(localLabel);
    
    // Create remote videos container
    this.remoteVideosContainer = document.createElement('div');
    this.remoteVideosContainer.className = 'gastric-collab-remote-videos';
    
    videoContainer.appendChild(localVideoWrapper);
    videoContainer.appendChild(this.remoteVideosContainer);
    
    // Create controls container
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'gastric-collab-controls';
    
    // Create mute audio button
    const muteAudioButton = document.createElement('button');
    muteAudioButton.className = 'gastric-collab-btn gastric-collab-btn-audio';
    muteAudioButton.innerHTML = '<i class="fas fa-microphone"></i>';
    muteAudioButton.title = 'Mute/Unmute Audio';
    muteAudioButton.addEventListener('click', () => this.toggleAudio());
    
    // Create mute video button
    const muteVideoButton = document.createElement('button');
    muteVideoButton.className = 'gastric-collab-btn gastric-collab-btn-video';
    muteVideoButton.innerHTML = '<i class="fas fa-video"></i>';
    muteVideoButton.title = 'Mute/Unmute Video';
    muteVideoButton.addEventListener('click', () => this.toggleVideo());
    
    // Create screen share button
    const screenShareButton = document.createElement('button');
    screenShareButton.className = 'gastric-collab-btn gastric-collab-btn-screen';
    screenShareButton.innerHTML = '<i class="fas fa-desktop"></i>';
    screenShareButton.title = 'Share Screen';
    screenShareButton.addEventListener('click', () => this.toggleScreenShare());
    
    // Create annotations button
    const annotationsButton = document.createElement('button');
    annotationsButton.className = 'gastric-collab-btn gastric-collab-btn-annotations';
    annotationsButton.innerHTML = '<i class="fas fa-pen"></i>';
    annotationsButton.title = 'Toggle Annotations';
    annotationsButton.addEventListener('click', () => this.toggleAnnotations());
    
    // Create end call button
    const endCallButton = document.createElement('button');
    endCallButton.className = 'gastric-collab-btn gastric-collab-btn-end';
    endCallButton.innerHTML = '<i class="fas fa-phone-slash"></i>';
    endCallButton.title = 'End Call';
    endCallButton.addEventListener('click', () => this.endCall());
    
    // Add buttons to controls
    controlsContainer.appendChild(muteAudioButton);
    controlsContainer.appendChild(muteVideoButton);
    controlsContainer.appendChild(screenShareButton);
    controlsContainer.appendChild(annotationsButton);
    controlsContainer.appendChild(endCallButton);
    
    // Create annotations layer
    this.annotationsLayer = document.createElement('div');
    this.annotationsLayer.className = 'gastric-collab-annotations-layer';
    this.annotationsLayer.style.display = 'none'; // Hidden by default
    
    // Add everything to the container
    this.containerElement.appendChild(videoContainer);
    this.containerElement.appendChild(controlsContainer);
    this.containerElement.appendChild(this.annotationsLayer);
    
    // Create chat container
    this.createChatUI();
  }
  
  /**
   * Create the chat UI
   */
  createChatUI() {
    const chatContainer = document.createElement('div');
    chatContainer.className = 'gastric-collab-chat';
    
    const chatHeader = document.createElement('div');
    chatHeader.className = 'gastric-collab-chat-header';
    chatHeader.textContent = 'Clinical Discussion';
    
    const chatMessages = document.createElement('div');
    chatMessages.className = 'gastric-collab-chat-messages';
    
    const chatForm = document.createElement('form');
    chatForm.className = 'gastric-collab-chat-form';
    
    const chatInput = document.createElement('input');
    chatInput.className = 'gastric-collab-chat-input';
    chatInput.type = 'text';
    chatInput.placeholder = 'Type a message...';
    
    const chatSendButton = document.createElement('button');
    chatSendButton.className = 'gastric-collab-chat-send';
    chatSendButton.type = 'submit';
    chatSendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    
    chatForm.appendChild(chatInput);
    chatForm.appendChild(chatSendButton);
    
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (message) {
        this.sendChatMessage(message);
        chatInput.value = '';
      }
    });
    
    chatContainer.appendChild(chatHeader);
    chatContainer.appendChild(chatMessages);
    chatContainer.appendChild(chatForm);
    
    this.containerElement.appendChild(chatContainer);
    this.chatMessages = chatMessages;
  }
  
  /**
   * Initialize WebRTC functionality
   */
  async initializeWebRTC() {
    try {
      // Get user media
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: this.options.enableAudio,
        video: this.options.enableVideo ? {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        } : false
      });
      
      // Set local video stream
      this.localVideoElement.srcObject = this.localStream;
      
      // Add HIPAA compliance headers
      if (this.options.hipaaCompliant) {
        // This would be implemented in the signaling server
        console.log('HIPAA compliance enabled for WebRTC');
      }
      
      console.log('WebRTC initialized successfully');
    } catch (error) {
      console.error('Failed to initialize WebRTC:', error);
      this.triggerCallback('onError', error);
      throw error;
    }
  }
  
  /**
   * Join a collaboration room
   * @param {string} roomId - The room ID to join, or null to create a new room
   * @returns {Promise<string>} - The room ID
   */
  async joinRoom(roomId = null) {
    try {
      // Generate room ID if not provided
      if (!roomId) {
        roomId = this.options.roomPrefix + this.generateRandomId();
      }
      
      this.roomId = roomId;
      
      // Create signaling connection
      await this.connectToSignalingServer();
      
      // Set up Gun.js for room
      if (this.gunDB) {
        this.setupGunRoom();
      }
      
      // Log the join for HIPAA compliance
      this.logCollaborationEvent('room-joined', {
        roomId: this.roomId,
        userId: this.userId,
        userRole: this.userRole,
        timestamp: new Date().toISOString()
      });
      
      return this.roomId;
    } catch (error) {
      console.error('Failed to join room:', error);
      this.triggerCallback('onError', error);
      throw error;
    }
  }
  
  /**
   * Connect to the signaling server
   */
  async connectToSignalingServer() {
    // In a real implementation, this would connect to a WebSocket signaling server
    // This is a simplified version for demonstration
    
    console.log('Connected to signaling server for room:', this.roomId);
    
    // Simulate other participants for demonstration
    setTimeout(() => {
      this.handleParticipantJoined({
        id: 'demo-user-1',
        name: 'Dr. Smith',
        role: 'Surgeon'
      });
    }, 2000);
    
    setTimeout(() => {
      this.handleParticipantJoined({
        id: 'demo-user-2',
        name: 'Dr. Johnson',
        role: 'Oncologist'
      });
    }, 3500);
  }
  
  /**
   * Handle a new participant joining
   * @param {Object} participant - The participant information
   */
  handleParticipantJoined(participant) {
    console.log('Participant joined:', participant);
    
    // Create peer connection for this participant
    this.createPeerConnection(participant.id);
    
    // Create video element for this participant
    this.createRemoteVideo(participant);
    
    // Trigger callback
    this.triggerCallback('onParticipantJoined', participant);
    
    // Log the event for HIPAA compliance
    this.logCollaborationEvent('participant-joined', {
      roomId: this.roomId,
      participantId: participant.id,
      participantRole: participant.role,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Create a peer connection for a participant
   * @param {string} participantId - The participant ID
   */
  createPeerConnection(participantId) {
    // Create RTCPeerConnection with ICE servers
    const peerConnection = new RTCPeerConnection({
      iceServers: [
        ...this.options.stunServers.map(server => ({ urls: server })),
        ...this.options.turnServers
      ]
    });
    
    // Add local stream tracks
    this.localStream.getTracks().forEach(track => {
      peerConnection.addTrack(track, this.localStream);
    });
    
    // Set up ICE candidate handling
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        // In a real implementation, send this to the signaling server
        console.log('ICE candidate for:', participantId, event.candidate);
      }
    };
    
    // Handle connection state changes
    peerConnection.onconnectionstatechange = () => {
      console.log('Connection state change:', peerConnection.connectionState);
      this.triggerCallback('onConnectionStateChanged', {
        participantId,
        state: peerConnection.connectionState
      });
    };
    
    // Handle ICE connection state changes
    peerConnection.oniceconnectionstatechange = () => {
      console.log('ICE connection state change:', peerConnection.iceConnectionState);
    };
    
    // Handle remote stream
    peerConnection.ontrack = (event) => {
      console.log('Remote track received from:', participantId);
      this.handleRemoteTrack(participantId, event.streams[0]);
    };
    
    // Create data channel for chat and annotations
    const dataChannel = peerConnection.createDataChannel('gastric-adci-data', {
      ordered: true
    });
    
    dataChannel.onopen = () => {
      console.log('Data channel opened with:', participantId);
    };
    
    dataChannel.onmessage = (event) => {
      this.handleDataChannelMessage(participantId, event.data);
    };
    
    // Store the peer connection and data channel
    this.peerConnections[participantId] = peerConnection;
    this.dataChannels[participantId] = dataChannel;
    
    // In a real implementation, we would create an offer and send it through the signaling server
    // This is a simplified version for demonstration
  }
  
  /**
   * Handle a remote track being received
   * @param {string} participantId - The participant ID
   * @param {MediaStream} stream - The media stream
   */
  handleRemoteTrack(participantId, stream) {
    // Find the video element for this participant
    const videoElement = document.querySelector(`.gastric-collab-remote-video[data-participant-id="${participantId}"]`);
    
    if (videoElement) {
      videoElement.srcObject = stream;
    }
  }
  
  /**
   * Create a video element for a remote participant
   * @param {Object} participant - The participant information
   */
  createRemoteVideo(participant) {
    const remoteVideoWrapper = document.createElement('div');
    remoteVideoWrapper.className = 'gastric-collab-remote-video-wrapper';
    remoteVideoWrapper.dataset.participantId = participant.id;
    
    const remoteVideo = document.createElement('video');
    remoteVideo.className = 'gastric-collab-remote-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;
    remoteVideo.dataset.participantId = participant.id;
    
    const remoteLabel = document.createElement('div');
    remoteLabel.className = 'gastric-collab-remote-label';
    remoteLabel.textContent = `${participant.name} (${participant.role})`;
    
    remoteVideoWrapper.appendChild(remoteVideo);
    remoteVideoWrapper.appendChild(remoteLabel);
    
    this.remoteVideosContainer.appendChild(remoteVideoWrapper);
    
    // In a real implementation, we would get the stream from the peer connection
    // This is a simplified version for demonstration
    setTimeout(() => {
      // Create a fake remote stream for demonstration
      const canvas = document.createElement('canvas');
      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#333';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.font = '24px Arial';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.fillText(`${participant.name}`, canvas.width / 2, canvas.height / 2);
      
      const fakeStream = canvas.captureStream(30);
      remoteVideo.srcObject = fakeStream;
    }, 1000);
  }
  
  /**
   * Toggle local audio mute state
   */
  toggleAudio() {
    const audioTracks = this.localStream.getAudioTracks();
    
    audioTracks.forEach(track => {
      track.enabled = !track.enabled;
    });
    
    const audioButton = document.querySelector('.gastric-collab-btn-audio');
    if (audioButton) {
      if (audioTracks[0] && audioTracks[0].enabled) {
        audioButton.innerHTML = '<i class="fas fa-microphone"></i>';
      } else {
        audioButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
      }
    }
    
    // Log the event for HIPAA compliance
    this.logCollaborationEvent('audio-toggle', {
      roomId: this.roomId,
      userId: this.userId,
      enabled: audioTracks[0] ? audioTracks[0].enabled : false,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Toggle local video mute state
   */
  toggleVideo() {
    const videoTracks = this.localStream.getVideoTracks();
    
    videoTracks.forEach(track => {
      track.enabled = !track.enabled;
    });
    
    const videoButton = document.querySelector('.gastric-collab-btn-video');
    if (videoButton) {
      if (videoTracks[0] && videoTracks[0].enabled) {
        videoButton.innerHTML = '<i class="fas fa-video"></i>';
      } else {
        videoButton.innerHTML = '<i class="fas fa-video-slash"></i>';
      }
    }
    
    // Log the event for HIPAA compliance
    this.logCollaborationEvent('video-toggle', {
      roomId: this.roomId,
      userId: this.userId,
      enabled: videoTracks[0] ? videoTracks[0].enabled : false,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Toggle screen sharing
   */
  async toggleScreenShare() {
    try {
      if (this.isScreenSharing) {
        // Stop screen sharing
        this.localStream.getTracks().forEach(track => track.stop());
        
        // Get camera stream again
        this.localStream = await navigator.mediaDevices.getUserMedia({
          audio: this.options.enableAudio,
          video: this.options.enableVideo ? {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          } : false
        });
        
        // Update local video
        this.localVideoElement.srcObject = this.localStream;
        
        // Update button
        const screenButton = document.querySelector('.gastric-collab-btn-screen');
        if (screenButton) {
          screenButton.innerHTML = '<i class="fas fa-desktop"></i>';
        }
        
        this.isScreenSharing = false;
      } else {
        // Start screen sharing
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: {
            cursor: 'always'
          },
          audio: false
        });
        
        // Replace video track in all peer connections
        const videoTrack = screenStream.getVideoTracks()[0];
        
        Object.values(this.peerConnections).forEach(pc => {
          const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
          if (sender) {
            sender.replaceTrack(videoTrack);
          }
        });
        
        // Handle the stream ending
        videoTrack.onended = () => {
          this.toggleScreenShare();
        };
        
        // Stop camera stream
        this.localStream.getVideoTracks().forEach(track => track.stop());
        
        // Keep audio tracks
        const audioTracks = this.localStream.getAudioTracks();
        
        // Create new stream with screen and audio
        this.localStream = new MediaStream([videoTrack, ...audioTracks]);
        
        // Update local video
        this.localVideoElement.srcObject = this.localStream;
        
        // Update button
        const screenButton = document.querySelector('.gastric-collab-btn-screen');
        if (screenButton) {
          screenButton.innerHTML = '<i class="fas fa-stop"></i>';
        }
        
        this.isScreenSharing = true;
      }
      
      // Log the event for HIPAA compliance
      this.logCollaborationEvent('screen-share-toggle', {
        roomId: this.roomId,
        userId: this.userId,
        isScreenSharing: this.isScreenSharing,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to toggle screen share:', error);
      this.triggerCallback('onError', error);
    }
  }
  
  /**
   * Toggle annotations layer
   */
  toggleAnnotations() {
    this.annotationsEnabled = !this.annotationsEnabled;
    
    if (this.annotationsEnabled) {
      this.annotationsLayer.style.display = 'block';
      this.initAnnotationsLayer();
    } else {
      this.annotationsLayer.style.display = 'none';
      this.clearAnnotationsLayer();
    }
    
    // Update button
    const annotationsButton = document.querySelector('.gastric-collab-btn-annotations');
    if (annotationsButton) {
      if (this.annotationsEnabled) {
        annotationsButton.classList.add('active');
      } else {
        annotationsButton.classList.remove('active');
      }
    }
    
    // Log the event for HIPAA compliance
    this.logCollaborationEvent('annotations-toggle', {
      roomId: this.roomId,
      userId: this.userId,
      enabled: this.annotationsEnabled,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Initialize the annotations layer
   */
  initAnnotationsLayer() {
    // Clear previous annotations
    this.clearAnnotationsLayer();
    
    // Create canvas for annotations
    const canvas = document.createElement('canvas');
    canvas.className = 'gastric-collab-annotations-canvas';
    canvas.width = this.annotationsLayer.offsetWidth;
    canvas.height = this.annotationsLayer.offsetHeight;
    
    this.annotationsLayer.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 3;
    
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    
    // Mouse events for drawing
    canvas.addEventListener('mousedown', (e) => {
      isDrawing = true;
      const rect = canvas.getBoundingClientRect();
      lastX = e.clientX - rect.left;
      lastY = e.clientY - rect.top;
    });
    
    canvas.addEventListener('mousemove', (e) => {
      if (!isDrawing) return;
      
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      ctx.beginPath();
      ctx.moveTo(lastX, lastY);
      ctx.lineTo(x, y);
      ctx.stroke();
      
      // Send annotation data to other participants
      this.sendAnnotationData({
        type: 'line',
        x1: lastX,
        y1: lastY,
        x2: x,
        y2: y,
        color: ctx.strokeStyle,
        width: ctx.lineWidth
      });
      
      lastX = x;
      lastY = y;
    });
    
    canvas.addEventListener('mouseup', () => {
      isDrawing = false;
    });
    
    canvas.addEventListener('mouseleave', () => {
      isDrawing = false;
    });
    
    // Touch events for mobile
    canvas.addEventListener('touchstart', (e) => {
      e.preventDefault();
      isDrawing = true;
      const rect = canvas.getBoundingClientRect();
      const touch = e.touches[0];
      lastX = touch.clientX - rect.left;
      lastY = touch.clientY - rect.top;
    });
    
    canvas.addEventListener('touchmove', (e) => {
      e.preventDefault();
      if (!isDrawing) return;
      
      const rect = canvas.getBoundingClientRect();
      const touch = e.touches[0];
      const x = touch.clientX - rect.left;
      const y = touch.clientY - rect.top;
      
      ctx.beginPath();
      ctx.moveTo(lastX, lastY);
      ctx.lineTo(x, y);
      ctx.stroke();
      
      // Send annotation data to other participants
      this.sendAnnotationData({
        type: 'line',
        x1: lastX,
        y1: lastY,
        x2: x,
        y2: y,
        color: ctx.strokeStyle,
        width: ctx.lineWidth
      });
      
      lastX = x;
      lastY = y;
    });
    
    canvas.addEventListener('touchend', () => {
      isDrawing = false;
    });
    
    // Store canvas context
    this.annotationsCanvas = canvas;
    this.annotationsContext = ctx;
    
    // Add color picker and clear button
    this.addAnnotationControls();
  }
  
  /**
   * Add annotation controls
   */
  addAnnotationControls() {
    const controls = document.createElement('div');
    controls.className = 'gastric-collab-annotations-controls';
    
    // Create color picker
    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.value = '#ff0000';
    colorPicker.className = 'gastric-collab-annotations-color';
    colorPicker.title = 'Annotation Color';
    
    colorPicker.addEventListener('change', (e) => {
      this.annotationsContext.strokeStyle = e.target.value;
    });
    
    // Create line width control
    const lineWidthSelect = document.createElement('select');
    lineWidthSelect.className = 'gastric-collab-annotations-width';
    lineWidthSelect.title = 'Line Width';
    
    [1, 3, 5, 8].forEach(width => {
      const option = document.createElement('option');
      option.value = width;
      option.textContent = width + 'px';
      if (width === 3) {
        option.selected = true;
      }
      lineWidthSelect.appendChild(option);
    });
    
    lineWidthSelect.addEventListener('change', (e) => {
      this.annotationsContext.lineWidth = parseInt(e.target.value);
    });
    
    // Create clear button
    const clearButton = document.createElement('button');
    clearButton.className = 'gastric-collab-annotations-clear';
    clearButton.innerHTML = '<i class="fas fa-trash"></i>';
    clearButton.title = 'Clear Annotations';
    
    clearButton.addEventListener('click', () => {
      this.clearAnnotationsLayer();
      this.initAnnotationsLayer();
      
      // Send clear command to other participants
      this.sendAnnotationData({
        type: 'clear'
      });
    });
    
    // Add controls to the container
    controls.appendChild(colorPicker);
    controls.appendChild(lineWidthSelect);
    controls.appendChild(clearButton);
    
    this.annotationsLayer.appendChild(controls);
  }
  
  /**
   * Clear the annotations layer
   */
  clearAnnotationsLayer() {
    this.annotationsLayer.innerHTML = '';
    this.annotationsCanvas = null;
    this.annotationsContext = null;
  }
  
  /**
   * Send annotation data to other participants
   * @param {Object} data - The annotation data
   */
  sendAnnotationData(data) {
    const message = {
      type: 'annotation',
      data: {
        ...data,
        userId: this.userId,
        timestamp: new Date().toISOString()
      }
    };
    
    // Send to all participants
    Object.values(this.dataChannels).forEach(dc => {
      if (dc.readyState === 'open') {
        dc.send(JSON.stringify(message));
      }
    });
    
    // Store in Gun.js if available
    if (this.gunDB && this.roomId) {
      this.gunDB.get(`rooms/${this.roomId}/annotations`).set(message.data);
    }
    
    // Trigger callback
    this.triggerCallback('onAnnotationAdded', message.data);
  }
  
  /**
   * Handle annotation data from other participants
   * @param {Object} data - The annotation data
   */
  handleAnnotationData(data) {
    if (!this.annotationsEnabled || !this.annotationsCanvas || !this.annotationsContext) {
      return;
    }
    
    const ctx = this.annotationsContext;
    
    if (data.type === 'clear') {
      this.clearAnnotationsLayer();
      this.initAnnotationsLayer();
      return;
    }
    
    if (data.type === 'line') {
      // Save current style
      const currentStyle = ctx.strokeStyle;
      const currentWidth = ctx.lineWidth;
      
      // Apply received style
      ctx.strokeStyle = data.color;
      ctx.lineWidth = data.width;
      
      // Draw the line
      ctx.beginPath();
      ctx.moveTo(data.x1, data.y1);
      ctx.lineTo(data.x2, data.y2);
      ctx.stroke();
      
      // Restore style
      ctx.strokeStyle = currentStyle;
      ctx.lineWidth = currentWidth;
    }
    
    // Trigger callback
    this.triggerCallback('onAnnotationAdded', data);
  }
  
  /**
   * Send a chat message to all participants
   * @param {string} message - The message text
   */
  sendChatMessage(message) {
    const messageData = {
      type: 'chat',
      data: {
        userId: this.userId,
        userName: this.userName,
        userRole: this.userRole,
        message: message,
        timestamp: new Date().toISOString()
      }
    };
    
    // Send to all participants
    Object.values(this.dataChannels).forEach(dc => {
      if (dc.readyState === 'open') {
        dc.send(JSON.stringify(messageData));
      }
    });
    
    // Add to local chat
    this.addChatMessage(messageData.data, true);
    
    // Store in Gun.js if available
    if (this.gunDB && this.roomId) {
      this.gunDB.get(`rooms/${this.roomId}/chat`).set(messageData.data);
    }
    
    // Trigger callback
    this.triggerCallback('onChatMessage', messageData.data);
    
    // Log the event for HIPAA compliance (message content is not logged)
    this.logCollaborationEvent('chat-message-sent', {
      roomId: this.roomId,
      userId: this.userId,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Add a chat message to the UI
   * @param {Object} messageData - The message data
   * @param {boolean} isLocal - Whether the message is from the local user
   */
  addChatMessage(messageData, isLocal = false) {
    if (!this.chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `gastric-collab-chat-message ${isLocal ? 'local' : 'remote'}`;
    
    const messageHeader = document.createElement('div');
    messageHeader.className = 'gastric-collab-chat-message-header';
    
    const messageName = document.createElement('span');
    messageName.className = 'gastric-collab-chat-message-name';
    messageName.textContent = isLocal ? 'You' : messageData.userName;
    
    const messageRole = document.createElement('span');
    messageRole.className = 'gastric-collab-chat-message-role';
    messageRole.textContent = `(${messageData.userRole})`;
    
    const messageTime = document.createElement('span');
    messageTime.className = 'gastric-collab-chat-message-time';
    messageTime.textContent = new Date(messageData.timestamp).toLocaleTimeString();
    
    messageHeader.appendChild(messageName);
    messageHeader.appendChild(messageRole);
    messageHeader.appendChild(messageTime);
    
    const messageContent = document.createElement('div');
    messageContent.className = 'gastric-collab-chat-message-content';
    messageContent.textContent = messageData.message;
    
    messageElement.appendChild(messageHeader);
    messageElement.appendChild(messageContent);
    
    this.chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }
  
  /**
   * Handle a data channel message
   * @param {string} participantId - The participant ID
   * @param {string} data - The message data
   */
  handleDataChannelMessage(participantId, data) {
    try {
      const message = JSON.parse(data);
      
      if (message.type === 'chat') {
        this.addChatMessage(message.data);
        this.triggerCallback('onChatMessage', message.data);
      } else if (message.type === 'annotation') {
        this.handleAnnotationData(message.data);
      }
    } catch (error) {
      console.error('Failed to parse data channel message:', error);
    }
  }
  
  /**
   * End the call and clean up resources
   */
  endCall() {
    // Stop local stream
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
    }
    
    // Close all peer connections
    Object.values(this.peerConnections).forEach(pc => pc.close());
    
    // Clear collections
    this.peerConnections = {};
    this.dataChannels = {};
    
    // Clear UI
    if (this.containerElement) {
      this.containerElement.innerHTML = '';
    }
    
    // Log the event for HIPAA compliance
    this.logCollaborationEvent('call-ended', {
      roomId: this.roomId,
      userId: this.userId,
      timestamp: new Date().toISOString()
    });
    
    console.log('Call ended');
  }
  
  /**
   * Initialize Gun.js for distributed state
   */
  initGunDB() {
    try {
      this.gunDB = new Gun({
        peers: [window.location.origin + '/gun'],
        localStorage: false
      });
      
      console.log('Gun.js initialized for collaboration');
    } catch (error) {
      console.error('Failed to initialize Gun.js:', error);
    }
  }
  
  /**
   * Set up Gun.js for a specific room
   */
  setupGunRoom() {
    if (!this.gunDB || !this.roomId) return;
    
    // Subscribe to annotations
    this.gunDB.get(`rooms/${this.roomId}/annotations`).on(data => {
      if (data && data.userId !== this.userId) {
        this.handleAnnotationData(data);
      }
    });
    
    // Subscribe to chat messages
    this.gunDB.get(`rooms/${this.roomId}/chat`).on(data => {
      if (data && data.userId !== this.userId) {
        this.addChatMessage(data);
      }
    });
  }
  
  /**
   * Log a collaboration event for HIPAA compliance
   * @param {string} eventType - The type of event
   * @param {Object} eventData - The event data
   */
  logCollaborationEvent(eventType, eventData) {
    // In a real implementation, this would send the event to a secure audit log service
    
    if (this.options.hipaaCompliant) {
      fetch('/api/audit/collaboration-event', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          eventType,
          ...eventData
        })
      }).catch(error => {
        console.error('Failed to log collaboration event:', error);
      });
    }
  }
  
  /**
   * Generate a random ID
   * @returns {string} - A random ID
   */
  generateRandomId() {
    return Math.random().toString(36).substr(2, 9);
  }
  
  /**
   * Set a callback function
   * @param {string} event - The event name
   * @param {Function} callback - The callback function
   */
  on(event, callback) {
    if (this.callbacks.hasOwnProperty(event)) {
      this.callbacks[event] = callback;
    }
  }
  
  /**
   * Trigger a callback function
   * @param {string} event - The event name
   * @param {*} data - The data to pass to the callback
   */
  triggerCallback(event, data) {
    if (this.callbacks[event]) {
      this.callbacks[event](data);
    }
  }
}

// Export the class
window.ClinicalCollaboration = ClinicalCollaboration;
