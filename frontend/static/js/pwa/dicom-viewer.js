/**
 * DICOM Viewer with MPR and 3D Visualization for Gastric ADCI Platform
 * Implements Cornerstone.js for advanced medical imaging
 */

class GastricDICOMViewer {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = {
      enableMPR: true,
      enable3D: true,
      enableAnnotations: true,
      enableMeasurements: true,
      syncWithCollaborators: true,
      ...options
    };
    
    this.viewports = {
      axial: null,
      sagittal: null,
      coronal: null,
      volume3D: null
    };
    
    this.tools = [];
    this.currentPatientId = null;
    this.currentSeriesId = null;
    this.currentStudyId = null;
    this.loadedInstances = [];
    this.collaborators = [];
    
    this.init();
  }
  
  async init() {
    try {
      // Initialize cornerstone and related libraries
      await this.initCornerstone();
      
      // Create the viewer UI
      this.createViewerUI();
      
      // Initialize tools
      this.initTools();
      
      // Set up WebRTC if collaboration is enabled
      if (this.options.syncWithCollaborators) {
        this.initCollaboration();
      }
      
      // Initialize Gun.js for distributed annotations
      this.initGunDB();
      
      console.log('DICOM Viewer initialized successfully');
    } catch (error) {
      console.error('Failed to initialize DICOM Viewer:', error);
    }
  }
  
  async initCornerstone() {
    // Wait for cornerstone to be fully loaded
    await new Promise(resolve => {
      const checkCornerstone = () => {
        if (window.cornerstone && 
            window.cornerstoneTools && 
            window.cornerstoneWADOImageLoader) {
          resolve();
        } else {
          setTimeout(checkCornerstone, 100);
        }
      };
      checkCornerstone();
    });
    
    // Configure cornerstone
    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
    cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
    
    // Configure for WADO-URI
    cornerstoneWADOImageLoader.configure({
      beforeSend: function(xhr) {
        // Add custom headers for HIPAA compliance
        xhr.setRequestHeader('X-ADCI-Audit-Trail', 'true');
      }
    });
    
    // Initialize cornerstone tools
    cornerstoneTools.init({
      showSVGCursors: true
    });
    
    // Enable HTML5 web workers
    cornerstoneWADOImageLoader.webWorkerManager.initialize({
      maxWebWorkers: navigator.hardwareConcurrency || 4,
      startWebWorkersOnDemand: true,
      taskConfiguration: {
        decodeTask: {
          loadCodecsOnStartup: true,
          initializeCodecsOnStartup: true
        }
      }
    });
  }
  
  createViewerUI() {
    // Clear the container
    this.container.innerHTML = '';
    
    // Create the MPR views
    const viewerLayout = document.createElement('div');
    viewerLayout.className = 'gastric-dicom-layout';
    
    // Create viewports based on options
    if (this.options.enableMPR) {
      // Create MPR viewports (axial, sagittal, coronal)
      const axialView = this.createViewport('axial', 'Axial');
      const sagittalView = this.createViewport('sagittal', 'Sagittal');
      const coronalView = this.createViewport('coronal', 'Coronal');
      
      viewerLayout.appendChild(axialView);
      viewerLayout.appendChild(sagittalView);
      viewerLayout.appendChild(coronalView);
    }
    
    if (this.options.enable3D) {
      // Create 3D volume rendering viewport
      const volumeView = this.createViewport('volume3D', '3D Volume');
      viewerLayout.appendChild(volumeView);
    }
    
    this.container.appendChild(viewerLayout);
    
    // Create toolbox
    this.createToolbox();
    
    // Apply responsive layout
    this.applyResponsiveLayout();
  }
  
  createViewport(id, label) {
    const viewportContainer = document.createElement('div');
    viewportContainer.className = 'gastric-dicom-viewport';
    viewportContainer.dataset.viewportType = id;
    
    const viewportLabel = document.createElement('div');
    viewportLabel.className = 'gastric-dicom-viewport-label';
    viewportLabel.textContent = label;
    
    const viewportCanvas = document.createElement('div');
    viewportCanvas.className = 'cornerstone-enabled-image';
    viewportCanvas.id = `viewport-${id}`;
    
    viewportContainer.appendChild(viewportLabel);
    viewportContainer.appendChild(viewportCanvas);
    
    // Store the viewport element
    this.viewports[id] = viewportCanvas;
    
    // Enable cornerstone on the element
    cornerstone.enable(viewportCanvas);
    
    return viewportContainer;
  }
  
  createToolbox() {
    const toolbox = document.createElement('div');
    toolbox.className = 'gastric-dicom-toolbox';
    
    // Create standard tools
    const toolGroups = [
      {
        name: 'Navigation',
        tools: ['Zoom', 'Pan', 'Scroll', 'Rotate', 'Reset']
      },
      {
        name: 'Measurements',
        tools: ['Length', 'Angle', 'Bidirectional', 'EllipticalROI', 'RectangleROI']
      },
      {
        name: 'Annotations',
        tools: ['ArrowAnnotate', 'TextMarker', 'FreehandROI']
      },
      {
        name: 'Visualization',
        tools: ['WindowLevel', 'Invert', 'MPRRotate', 'VolumeRotate', 'Crosshairs']
      },
      {
        name: 'Surgical Planning',
        tools: ['SurgicalPath', 'TumorMargin', 'LymphNodeMapping']
      }
    ];
    
    toolGroups.forEach(group => {
      const toolGroup = document.createElement('div');
      toolGroup.className = 'gastric-dicom-tool-group';
      
      const toolGroupTitle = document.createElement('h3');
      toolGroupTitle.textContent = group.name;
      toolGroup.appendChild(toolGroupTitle);
      
      const toolButtons = document.createElement('div');
      toolButtons.className = 'gastric-dicom-tool-buttons';
      
      group.tools.forEach(toolName => {
        const toolButton = document.createElement('button');
        toolButton.className = 'gastric-dicom-tool-btn';
        toolButton.dataset.tool = toolName.toLowerCase();
        toolButton.title = toolName;
        toolButton.textContent = toolName;
        
        toolButton.addEventListener('click', () => this.activateTool(toolName.toLowerCase()));
        
        toolButtons.appendChild(toolButton);
      });
      
      toolGroup.appendChild(toolButtons);
      toolbox.appendChild(toolGroup);
    });
    
    this.container.appendChild(toolbox);
  }
  
  initTools() {
    // Register all tools
    const tools = [
      cornerstoneTools.ZoomTool,
      cornerstoneTools.PanTool,
      cornerstoneTools.StackScrollTool,
      cornerstoneTools.RotateTool,
      cornerstoneTools.LengthTool,
      cornerstoneTools.AngleTool,
      cornerstoneTools.BidirectionalTool,
      cornerstoneTools.EllipticalRoiTool,
      cornerstoneTools.RectangleRoiTool,
      cornerstoneTools.ArrowAnnotateTool,
      cornerstoneTools.TextMarkerTool,
      cornerstoneTools.FreehandRoiTool,
      cornerstoneTools.WwwcTool,
      cornerstoneTools.InvertTool,
      cornerstoneTools.CrosshairsTool,
      // Custom tools would be added here
    ];
    
    tools.forEach(tool => {
      cornerstoneTools.addTool(tool);
    });
    
    // Set initial tool
    Object.values(this.viewports).forEach(viewport => {
      if (viewport) {
        cornerstoneTools.setToolActiveForElement(viewport, 'Zoom', { mouseButtonMask: 1 });
      }
    });
  }
  
  activateTool(toolName) {
    // Deactivate all tools
    const toolButtons = document.querySelectorAll('.gastric-dicom-tool-btn');
    toolButtons.forEach(button => button.classList.remove('active'));
    
    // Activate the selected tool
    const selectedButton = document.querySelector(`.gastric-dicom-tool-btn[data-tool="${toolName}"]`);
    if (selectedButton) {
      selectedButton.classList.add('active');
    }
    
    // Map tool names to cornerstone tool names
    const toolMap = {
      'zoom': 'Zoom',
      'pan': 'Pan',
      'scroll': 'StackScroll',
      'rotate': 'Rotate',
      'length': 'Length',
      'angle': 'Angle',
      'bidirectional': 'Bidirectional',
      'ellipticalroi': 'EllipticalRoi',
      'rectangleroi': 'RectangleRoi',
      'arrowannotate': 'ArrowAnnotate',
      'textmarker': 'TextMarker',
      'freehandroi': 'FreehandRoi',
      'windowlevel': 'Wwwc',
      'invert': 'Invert',
      'crosshairs': 'Crosshairs',
      // Add mappings for custom tools
    };
    
    const cornerstoneTool = toolMap[toolName] || toolName;
    
    // Set the tool active on all viewports
    Object.values(this.viewports).forEach(viewport => {
      if (viewport) {
        cornerstoneTools.setToolActiveForElement(viewport, cornerstoneTool, { mouseButtonMask: 1 });
      }
    });
  }
  
  async loadStudy(patientId, studyId) {
    this.currentPatientId = patientId;
    this.currentStudyId = studyId;
    
    try {
      const studyMetadata = await this.fetchStudyMetadata(patientId, studyId);
      
      // Check if we have series data
      if (!studyMetadata || !studyMetadata.series || studyMetadata.series.length === 0) {
        throw new Error('No imaging series found in this study');
      }
      
      // Load the first series by default
      await this.loadSeries(studyMetadata.series[0].seriesId);
      
      return true;
    } catch (error) {
      console.error('Failed to load study:', error);
      this.showError(`Failed to load study: ${error.message}`);
      return false;
    }
  }
  
  async loadSeries(seriesId) {
    this.currentSeriesId = seriesId;
    
    try {
      // Show loading indicator
      this.showLoading(true);
      
      // Fetch the series metadata
      const seriesMetadata = await this.fetchSeriesMetadata(this.currentPatientId, this.currentStudyId, seriesId);
      
      // Load instances
      const instancePromises = seriesMetadata.instances.map(instance => 
        this.loadInstance(instance.instanceId));
      
      this.loadedInstances = await Promise.all(instancePromises);
      
      // Initialize MPR if enabled
      if (this.options.enableMPR && this.loadedInstances.length > 0) {
        await this.initializeMPR();
      }
      
      // Initialize 3D if enabled
      if (this.options.enable3D && this.loadedInstances.length > 0) {
        await this.initialize3DVolume();
      }
      
      // Hide loading indicator
      this.showLoading(false);
      
      return true;
    } catch (error) {
      console.error('Failed to load series:', error);
      this.showError(`Failed to load series: ${error.message}`);
      this.showLoading(false);
      return false;
    }
  }
  
  async fetchStudyMetadata(patientId, studyId) {
    const response = await fetch(`/api/dicom/patients/${patientId}/studies/${studyId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  }
  
  async fetchSeriesMetadata(patientId, studyId, seriesId) {
    const response = await fetch(`/api/dicom/patients/${patientId}/studies/${studyId}/series/${seriesId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  }
  
  async loadInstance(instanceId) {
    const imageId = `wadouri:/api/dicom/instances/${instanceId}`;
    return await cornerstone.loadAndCacheImage(imageId);
  }
  
  async initializeMPR() {
    // Set up MPR views (axial, sagittal, coronal)
    if (this.viewports.axial) {
      cornerstone.displayImage(this.viewports.axial, this.loadedInstances[0]);
    }
    
    // In a real implementation, we would compute the sagittal and coronal reformats
    // This is a simplified version
    if (this.viewports.sagittal && this.loadedInstances.length > 1) {
      cornerstone.displayImage(this.viewports.sagittal, this.loadedInstances[Math.floor(this.loadedInstances.length / 3)]);
    }
    
    if (this.viewports.coronal && this.loadedInstances.length > 2) {
      cornerstone.displayImage(this.viewports.coronal, this.loadedInstances[Math.floor(this.loadedInstances.length * 2 / 3)]);
    }
    
    // Enable synchronized scrolling
    this.enableSynchronization();
  }
  
  async initialize3DVolume() {
    if (!this.viewports.volume3D || this.loadedInstances.length === 0) {
      return;
    }
    
    // In a real implementation, we would use Cornerstone3D or VTK.js for volume rendering
    // This is a placeholder for the actual implementation
    
    const volumeCanvas = document.createElement('canvas');
    volumeCanvas.width = this.viewports.volume3D.offsetWidth;
    volumeCanvas.height = this.viewports.volume3D.offsetHeight;
    
    const ctx = volumeCanvas.getContext('2d');
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, volumeCanvas.width, volumeCanvas.height);
    ctx.font = '14px Arial';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.fillText('3D Volume Rendering (Placeholder)', volumeCanvas.width / 2, volumeCanvas.height / 2);
    
    this.viewports.volume3D.innerHTML = '';
    this.viewports.volume3D.appendChild(volumeCanvas);
  }
  
  enableSynchronization() {
    // Set up synchronization between viewports
    const synchronizer = new cornerstoneTools.Synchronizer(
      'cornerstoneNewImage',
      cornerstoneTools.stackImagePositionSynchronizer
    );
    
    // Add each element to the synchronizer
    Object.values(this.viewports).forEach(viewport => {
      if (viewport && viewport.id !== 'viewport-volume3D') {
        synchronizer.add(viewport);
      }
    });
    
    // Activate synchronizer
    synchronizer.enabled = true;
  }
  
  initCollaboration() {
    // Initialize WebRTC for collaboration
    // This would be implemented using the webrtc-collab.js module
    console.log('Initializing collaboration features');
  }
  
  initGunDB() {
    // Initialize Gun.js for distributed annotations
    if (window.Gun) {
      this.gun = new Gun({
        peers: [window.location.origin + '/gun'],
        localStorage: false
      });
      
      // Set up annotation syncing
      this.annotationsDB = this.gun.get('gastric-annotations');
    }
  }
  
  syncAnnotations() {
    if (!this.gun || !this.currentSeriesId) return;
    
    // Get current annotations
    const annotations = this.getAllAnnotations();
    
    // Store in Gun.js
    this.annotationsDB.get(this.currentSeriesId).put(annotations);
    
    // Subscribe to changes
    this.annotationsDB.get(this.currentSeriesId).on(data => {
      if (data && !this.isCurrentUserChange) {
        this.loadAnnotationsFromData(data);
      }
    });
  }
  
  getAllAnnotations() {
    // Get all annotations from cornerstone tools
    // This is a simplified version
    return {
      timestamp: new Date().toISOString(),
      userId: this.getCurrentUserId(),
      annotations: []
    };
  }
  
  loadAnnotationsFromData(data) {
    // Load annotations from data
    console.log('Loading annotations from collaborator', data);
  }
  
  getCurrentUserId() {
    // Get the current user ID from the application
    return 'user-123'; // Placeholder
  }
  
  showLoading(show) {
    // Show or hide loading indicator
    const loadingElement = document.querySelector('.gastric-dicom-loading');
    
    if (show) {
      if (!loadingElement) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'gastric-dicom-loading';
        loadingDiv.innerHTML = '<div class="spinner"></div><p>Loading DICOM data...</p>';
        this.container.appendChild(loadingDiv);
      }
    } else if (loadingElement) {
      loadingElement.remove();
    }
  }
  
  showError(message) {
    // Show error message
    const errorElement = document.querySelector('.gastric-dicom-error');
    
    if (errorElement) {
      errorElement.remove();
    }
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'gastric-dicom-error';
    errorDiv.innerHTML = `<p>${message}</p><button class="error-close">Close</button>`;
    
    const closeButton = errorDiv.querySelector('.error-close');
    closeButton.addEventListener('click', () => errorDiv.remove());
    
    this.container.appendChild(errorDiv);
  }
  
  applyResponsiveLayout() {
    // Apply responsive layout based on container size
    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        
        if (width < 768) {
          this.container.classList.add('gastric-dicom-small');
          this.container.classList.remove('gastric-dicom-medium', 'gastric-dicom-large');
        } else if (width < 1200) {
          this.container.classList.add('gastric-dicom-medium');
          this.container.classList.remove('gastric-dicom-small', 'gastric-dicom-large');
        } else {
          this.container.classList.add('gastric-dicom-large');
          this.container.classList.remove('gastric-dicom-small', 'gastric-dicom-medium');
        }
      }
    });
    
    resizeObserver.observe(this.container);
  }
  
  // Public API
  
  /**
   * Load a patient's DICOM study
   * @param {string} patientId - The patient ID
   * @param {string} studyId - The study ID
   * @returns {Promise<boolean>} - Whether the load was successful
   */
  async loadPatientStudy(patientId, studyId) {
    return await this.loadStudy(patientId, studyId);
  }
  
  /**
   * Export annotations as a DICOM-SR compatible format
   * @returns {Object} - The exported annotations
   */
  exportAnnotations() {
    // Export annotations in a DICOM-SR compatible format
    return {
      patientId: this.currentPatientId,
      studyId: this.currentStudyId,
      seriesId: this.currentSeriesId,
      annotations: this.getAllAnnotations(),
      exportDate: new Date().toISOString(),
      user: this.getCurrentUserId()
    };
  }
  
  /**
   * Save the current state to the surgical plan
   * @returns {Promise<boolean>} - Whether the save was successful
   */
  async saveToSurgicalPlan() {
    try {
      const annotations = this.exportAnnotations();
      
      const response = await fetch(`/api/patients/${this.currentPatientId}/surgical-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          dicomAnnotations: annotations,
          timestamp: new Date().toISOString()
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return true;
    } catch (error) {
      console.error('Failed to save to surgical plan:', error);
      this.showError(`Failed to save: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Destroy the viewer and clean up resources
   */
  destroy() {
    // Clean up cornerstone resources
    Object.values(this.viewports).forEach(viewport => {
      if (viewport) {
        cornerstone.disable(viewport);
      }
    });
    
    // Clean up other resources
    if (this.gun) {
      this.gun.off();
    }
    
    // Clear the container
    this.container.innerHTML = '';
  }
}

// Export the viewer class
window.GastricDICOMViewer = GastricDICOMViewer;
