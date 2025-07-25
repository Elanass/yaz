/**
 * WebXR-based AR Visualization for Gastric ADCI Platform
 * Provides augmented reality visualization for surgical planning and education
 */

class GastricARVisualization {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      throw new Error(`Container element with ID ${containerId} not found`);
    }
    
    this.options = {
      modelPath: '/static/models/gastric_anatomy/',
      enableHapticFeedback: true,
      showLabels: true,
      interactiveMode: true,
      surgicalPlanningMode: false,
      enableMeasurements: true,
      qualityLevel: 'high',
      ...options
    };
    
    this.isSupported = false;
    this.isInitialized = false;
    this.isInARMode = false;
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.xrSession = null;
    this.reticle = null;
    this.models = {};
    this.anchors = {};
    this.measurements = [];
    this.currentModelId = null;
    this.surgicalPlan = null;
    
    // Check WebXR support
    this.checkXRSupport();
  }
  
  /**
   * Check if WebXR is supported
   */
  async checkXRSupport() {
    // Check if WebXR is available
    if ('xr' in navigator) {
      try {
        // Check if immersive-ar mode is supported
        this.isSupported = await navigator.xr.isSessionSupported('immersive-ar');
        
        if (this.isSupported) {
          console.log('WebXR AR is supported');
          this.createUI();
        } else {
          console.warn('WebXR AR is not supported on this device');
          this.showUnsupportedMessage();
        }
      } catch (error) {
        console.error('Error checking WebXR support:', error);
        this.isSupported = false;
        this.showUnsupportedMessage();
      }
    } else {
      console.warn('WebXR not available in this browser');
      
      // Try to load polyfill
      if (!this.options.disablePolyfill) {
        this.loadWebXRPolyfill();
      } else {
        this.showUnsupportedMessage();
      }
    }
  }
  
  /**
   * Load WebXR polyfill
   */
  loadWebXRPolyfill() {
    const script = document.createElement('script');
    script.src = '/static/js/webxr-polyfill.min.js';
    script.onload = () => {
      if (window.WebXRPolyfill) {
        new WebXRPolyfill();
        this.checkXRSupport(); // Check again after polyfill loaded
      }
    };
    document.head.appendChild(script);
  }
  
  /**
   * Create the AR UI
   */
  createUI() {
    // Clear the container
    this.container.innerHTML = '';
    this.container.className = 'gastric-ar-container';
    
    // Create AR button
    const arButton = document.createElement('button');
    arButton.className = 'gastric-ar-start-btn';
    arButton.innerHTML = '<i class="fas fa-vr-cardboard"></i> Start AR Visualization';
    arButton.addEventListener('click', () => this.startAR());
    
    // Create model selection UI
    const modelSelector = document.createElement('div');
    modelSelector.className = 'gastric-ar-model-selector';
    
    const modelSelectorLabel = document.createElement('h3');
    modelSelectorLabel.textContent = 'Select Anatomical Model';
    modelSelector.appendChild(modelSelectorLabel);
    
    const modelList = document.createElement('div');
    modelList.className = 'gastric-ar-model-list';
    
    // Add models to the list
    const models = [
      { id: 'stomach_full', name: 'Complete Gastric Anatomy', type: 'anatomy' },
      { id: 'stomach_layers', name: 'Stomach Wall Layers', type: 'anatomy' },
      { id: 'lymph_nodes', name: 'Lymphatic Drainage', type: 'anatomy' },
      { id: 'blood_supply', name: 'Vascular Supply', type: 'anatomy' },
      { id: 'tumor_t1', name: 'T1 Tumor Visualization', type: 'pathology' },
      { id: 'tumor_t2', name: 'T2 Tumor Visualization', type: 'pathology' },
      { id: 'tumor_t3', name: 'T3 Tumor Visualization', type: 'pathology' },
      { id: 'tumor_t4', name: 'T4 Tumor Visualization', type: 'pathology' },
      { id: 'gastrectomy_total', name: 'Total Gastrectomy', type: 'procedure' },
      { id: 'gastrectomy_subtotal', name: 'Subtotal Gastrectomy', type: 'procedure' },
      { id: 'gastrectomy_proximal', name: 'Proximal Gastrectomy', type: 'procedure' },
      { id: 'lymphadenectomy_d2', name: 'D2 Lymphadenectomy', type: 'procedure' }
    ];
    
    models.forEach(model => {
      const modelItem = document.createElement('div');
      modelItem.className = 'gastric-ar-model-item';
      modelItem.dataset.modelId = model.id;
      modelItem.dataset.modelType = model.type;
      
      const modelName = document.createElement('span');
      modelName.textContent = model.name;
      
      modelItem.appendChild(modelName);
      modelItem.addEventListener('click', () => {
        // Select this model
        document.querySelectorAll('.gastric-ar-model-item').forEach(item => {
          item.classList.remove('selected');
        });
        modelItem.classList.add('selected');
        this.currentModelId = model.id;
      });
      
      modelList.appendChild(modelItem);
    });
    
    modelSelector.appendChild(modelList);
    
    // Create filter buttons
    const filterButtons = document.createElement('div');
    filterButtons.className = 'gastric-ar-filters';
    
    ['All', 'Anatomy', 'Pathology', 'Procedure'].forEach(filter => {
      const button = document.createElement('button');
      button.className = 'gastric-ar-filter-btn';
      if (filter === 'All') {
        button.classList.add('active');
      }
      button.textContent = filter;
      button.addEventListener('click', () => {
        // Apply filter
        document.querySelectorAll('.gastric-ar-filter-btn').forEach(btn => {
          btn.classList.remove('active');
        });
        button.classList.add('active');
        
        if (filter === 'All') {
          document.querySelectorAll('.gastric-ar-model-item').forEach(item => {
            item.style.display = 'flex';
          });
        } else {
          const filterType = filter.toLowerCase();
          document.querySelectorAll('.gastric-ar-model-item').forEach(item => {
            if (item.dataset.modelType === filterType) {
              item.style.display = 'flex';
            } else {
              item.style.display = 'none';
            }
          });
        }
      });
      
      filterButtons.appendChild(button);
    });
    
    modelSelector.appendChild(filterButtons);
    
    // Create preview canvas
    const previewContainer = document.createElement('div');
    previewContainer.className = 'gastric-ar-preview';
    
    const previewCanvas = document.createElement('canvas');
    previewCanvas.className = 'gastric-ar-preview-canvas';
    previewCanvas.width = 300;
    previewCanvas.height = 300;
    
    previewContainer.appendChild(previewCanvas);
    
    // Add components to the container
    this.container.appendChild(arButton);
    this.container.appendChild(modelSelector);
    this.container.appendChild(previewContainer);
    
    // Initialize Three.js for preview
    this.initializePreview(previewCanvas);
    
    // Select the first model by default
    document.querySelector('.gastric-ar-model-item').classList.add('selected');
    this.currentModelId = models[0].id;
  }
  
  /**
   * Initialize Three.js for model preview
   * @param {HTMLCanvasElement} canvas - The canvas element
   */
  initializePreview(canvas) {
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 0.1, 1000);
    camera.position.z = 3;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true
    });
    renderer.setSize(canvas.width, canvas.height);
    
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    // Add directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Add a placeholder model (sphere)
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshStandardMaterial({
      color: 0xf96854,
      metalness: 0.1,
      roughness: 0.5
    });
    const sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);
    
    // Add rotation animation
    const animate = () => {
      requestAnimationFrame(animate);
      
      sphere.rotation.x += 0.01;
      sphere.rotation.y += 0.01;
      
      renderer.render(scene, camera);
    };
    
    animate();
    
    // Store references
    this.previewScene = scene;
    this.previewCamera = camera;
    this.previewRenderer = renderer;
    this.previewModel = sphere;
  }
  
  /**
   * Show message when WebXR is not supported
   */
  showUnsupportedMessage() {
    // Clear the container
    this.container.innerHTML = '';
    
    const message = document.createElement('div');
    message.className = 'gastric-ar-unsupported';
    
    const icon = document.createElement('div');
    icon.className = 'gastric-ar-unsupported-icon';
    icon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
    
    const title = document.createElement('h3');
    title.textContent = 'AR Not Supported';
    
    const description = document.createElement('p');
    description.textContent = 'Augmented Reality is not supported on this device or browser. Please use a compatible device with ARCore (Android) or ARKit (iOS) support.';
    
    const alternativeButton = document.createElement('button');
    alternativeButton.className = 'gastric-ar-alternative-btn';
    alternativeButton.textContent = 'Use 3D Viewer Instead';
    alternativeButton.addEventListener('click', () => {
      this.switchTo3DViewer();
    });
    
    message.appendChild(icon);
    message.appendChild(title);
    message.appendChild(description);
    message.appendChild(alternativeButton);
    
    this.container.appendChild(message);
  }
  
  /**
   * Switch to 3D viewer as fallback
   */
  switchTo3DViewer() {
    // Clear the container
    this.container.innerHTML = '';
    
    const viewer3DCanvas = document.createElement('canvas');
    viewer3DCanvas.className = 'gastric-3d-viewer-canvas';
    viewer3DCanvas.width = this.container.clientWidth;
    viewer3DCanvas.height = this.container.clientHeight;
    
    this.container.appendChild(viewer3DCanvas);
    
    // Initialize Three.js for 3D viewer
    this.initialize3DViewer(viewer3DCanvas);
  }
  
  /**
   * Initialize Three.js for 3D viewer fallback
   * @param {HTMLCanvasElement} canvas - The canvas element
   */
  initialize3DViewer(canvas) {
    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 0.1, 1000);
    camera.position.z = 5;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true
    });
    renderer.setSize(canvas.width, canvas.height);
    
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    // Add directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Add orbital controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    // Load model based on current selection
    this.load3DModel(scene, this.currentModelId || 'stomach_full');
    
    // Add animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    
    animate();
    
    // Handle resize
    window.addEventListener('resize', () => {
      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      
      renderer.setSize(width, height);
    });
    
    // Store references
    this.fallbackScene = scene;
    this.fallbackCamera = camera;
    this.fallbackRenderer = renderer;
    this.fallbackControls = controls;
  }
  
  /**
   * Load a 3D model into the scene
   * @param {THREE.Scene} scene - The Three.js scene
   * @param {string} modelId - The model ID to load
   */
  load3DModel(scene, modelId) {
    // Clear previous models
    scene.children = scene.children.filter(child => !(child instanceof THREE.Mesh));
    
    // Create a placeholder model for demonstration
    let geometry, material, mesh;
    
    if (modelId === 'stomach_full') {
      geometry = new THREE.TorusGeometry(2, 0.5, 16, 50);
      material = new THREE.MeshStandardMaterial({
        color: 0xf96854,
        metalness: 0.1,
        roughness: 0.5
      });
    } else if (modelId.startsWith('tumor')) {
      geometry = new THREE.SphereGeometry(1, 32, 32);
      material = new THREE.MeshStandardMaterial({
        color: 0xff0000,
        metalness: 0.1,
        roughness: 0.5
      });
    } else if (modelId.startsWith('gastrectomy')) {
      geometry = new THREE.CylinderGeometry(1, 1, 2, 32);
      material = new THREE.MeshStandardMaterial({
        color: 0x00aaff,
        metalness: 0.1,
        roughness: 0.5
      });
    } else if (modelId === 'lymph_nodes') {
      // Create multiple small spheres for lymph nodes
      const group = new THREE.Group();
      
      for (let i = 0; i < 15; i++) {
        const nodeGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const nodeMaterial = new THREE.MeshStandardMaterial({
          color: 0x88ff88,
          metalness: 0.1,
          roughness: 0.5
        });
        
        const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
        node.position.set(
          Math.random() * 4 - 2,
          Math.random() * 4 - 2,
          Math.random() * 4 - 2
        );
        
        group.add(node);
      }
      
      scene.add(group);
      return;
    } else {
      geometry = new THREE.BoxGeometry(2, 2, 2);
      material = new THREE.MeshStandardMaterial({
        color: 0xaaaaaa,
        metalness: 0.1,
        roughness: 0.5
      });
    }
    
    mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    
    // In a real implementation, we would load actual models using GLTFLoader
    // Example:
    // const loader = new THREE.GLTFLoader();
    // loader.load(`${this.options.modelPath}${modelId}.glb`, (gltf) => {
    //   scene.add(gltf.scene);
    // });
  }
  
  /**
   * Start AR experience
   */
  async startAR() {
    if (!this.isSupported) {
      console.warn('WebXR AR is not supported on this device');
      return;
    }
    
    try {
      // Initialize Three.js if not already done
      if (!this.isInitialized) {
        await this.initializeAR();
      }
      
      // Request AR session
      this.xrSession = await navigator.xr.requestSession('immersive-ar', {
        requiredFeatures: ['hit-test', 'anchors'],
        optionalFeatures: ['dom-overlay'],
        domOverlay: { root: this.createAROverlay() }
      });
      
      // Set up session
      this.xrSession.addEventListener('end', () => {
        this.isInARMode = false;
        this.onARSessionEnded();
      });
      
      // Set up WebXR rendering
      this.bindXRToRenderer();
      
      // Start AR rendering
      this.isInARMode = true;
      
      // Log session start for compliance
      this.logAREvent('session-started', {
        modelId: this.currentModelId,
        timestamp: new Date().toISOString()
      });
      
      console.log('AR session started');
    } catch (error) {
      console.error('Failed to start AR session:', error);
      this.showError('Failed to start AR session: ' + error.message);
    }
  }
  
  /**
   * Initialize AR with Three.js
   */
  async initializeAR() {
    // Create scene
    this.scene = new THREE.Scene();
    
    // Create camera (will be updated by WebXR)
    this.camera = new THREE.PerspectiveCamera();
    
    // Create renderer with WebXR support
    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      preserveDrawingBuffer: true // For capturing screenshots
    });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.xr.enabled = true;
    
    // Add the renderer to the container
    this.container.appendChild(this.renderer.domElement);
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    this.scene.add(directionalLight);
    
    // Create a reticle for hit testing
    const reticleGeometry = new THREE.RingGeometry(0.15, 0.2, 32);
    const reticleMaterial = new THREE.MeshBasicMaterial({ color: 0x0096ff });
    this.reticle = new THREE.Mesh(reticleGeometry, reticleMaterial);
    this.reticle.rotation.x = -Math.PI / 2;
    this.reticle.visible = false;
    this.scene.add(this.reticle);
    
    // Load models (preload)
    await this.preloadModels();
    
    this.isInitialized = true;
    console.log('AR initialized');
  }
  
  /**
   * Create an overlay for AR mode
   */
  createAROverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'gastric-ar-overlay';
    
    // Add buttons
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'gastric-ar-overlay-buttons';
    
    const placeButton = document.createElement('button');
    placeButton.className = 'gastric-ar-place-btn';
    placeButton.innerHTML = '<i class="fas fa-plus"></i> Place Model';
    placeButton.addEventListener('click', () => this.placeModel());
    
    const exitButton = document.createElement('button');
    exitButton.className = 'gastric-ar-exit-btn';
    exitButton.innerHTML = '<i class="fas fa-times"></i> Exit AR';
    exitButton.addEventListener('click', () => this.endARSession());
    
    buttonsContainer.appendChild(placeButton);
    buttonsContainer.appendChild(exitButton);
    
    // Add model selector
    const modelSelectorMini = document.createElement('div');
    modelSelectorMini.className = 'gastric-ar-model-selector-mini';
    
    // Add selected model name
    const selectedModelName = document.createElement('div');
    selectedModelName.className = 'gastric-ar-selected-model';
    selectedModelName.textContent = this.getModelNameById(this.currentModelId);
    
    modelSelectorMini.appendChild(selectedModelName);
    
    // Add information panel
    const infoPanel = document.createElement('div');
    infoPanel.className = 'gastric-ar-info-panel';
    infoPanel.textContent = 'Move your device to scan the environment. Tap "Place Model" when the reticle appears.';
    
    overlay.appendChild(buttonsContainer);
    overlay.appendChild(modelSelectorMini);
    overlay.appendChild(infoPanel);
    
    return overlay;
  }
  
  /**
   * Get model name from ID
   * @param {string} modelId - The model ID
   * @returns {string} - The model name
   */
  getModelNameById(modelId) {
    const models = {
      'stomach_full': 'Complete Gastric Anatomy',
      'stomach_layers': 'Stomach Wall Layers',
      'lymph_nodes': 'Lymphatic Drainage',
      'blood_supply': 'Vascular Supply',
      'tumor_t1': 'T1 Tumor Visualization',
      'tumor_t2': 'T2 Tumor Visualization',
      'tumor_t3': 'T3 Tumor Visualization',
      'tumor_t4': 'T4 Tumor Visualization',
      'gastrectomy_total': 'Total Gastrectomy',
      'gastrectomy_subtotal': 'Subtotal Gastrectomy',
      'gastrectomy_proximal': 'Proximal Gastrectomy',
      'lymphadenectomy_d2': 'D2 Lymphadenectomy'
    };
    
    return models[modelId] || 'Unknown Model';
  }
  
  /**
   * Bind WebXR to Three.js renderer
   */
  bindXRToRenderer() {
    const session = this.xrSession;
    const renderer = this.renderer;
    
    // Create XR reference space
    session.requestReferenceSpace('local').then(referenceSpace => {
      this.xrReferenceSpace = referenceSpace;
      
      // Set up hit testing
      session.requestReferenceSpace('viewer').then(viewerReferenceSpace => {
        this.xrViewerReferenceSpace = viewerReferenceSpace;
        
        session.requestHitTestSource({
          space: viewerReferenceSpace
        }).then(hitTestSource => {
          this.xrHitTestSource = hitTestSource;
        });
      });
      
      // Start render loop
      renderer.setAnimationLoop(this.xrRenderLoop.bind(this));
    });
    
    // Prepare XR GL layer
    const gl = renderer.getContext();
    const baseLayer = new XRWebGLLayer(session, gl);
    session.updateRenderState({ baseLayer });
  }
  
  /**
   * WebXR render loop
   * @param {DOMHighResTimeStamp} time - The current time
   * @param {XRFrame} frame - The XR frame
   */
  xrRenderLoop(time, frame) {
    if (!this.isInARMode || !frame) return;
    
    const session = this.xrSession;
    const referenceSpace = this.xrReferenceSpace;
    
    // Get viewer pose
    const pose = frame.getViewerPose(referenceSpace);
    if (pose) {
      // Update camera with viewer pose
      const view = pose.views[0];
      const viewport = this.renderer.getContext().getViewport();
      
      viewport.width = view.resolution.width;
      viewport.height = view.resolution.height;
      
      this.camera.matrix.fromArray(view.transform.matrix);
      this.camera.matrix.decompose(this.camera.position, this.camera.quaternion, this.camera.scale);
      this.camera.projectionMatrix.fromArray(view.projectionMatrix);
      
      // Handle hit testing
      if (this.xrHitTestSource) {
        const hitTestResults = frame.getHitTestResults(this.xrHitTestSource);
        
        if (hitTestResults.length > 0) {
          const hit = hitTestResults[0];
          const hitPose = hit.getPose(referenceSpace);
          
          // Update reticle position
          if (hitPose) {
            this.reticle.visible = true;
            this.reticle.position.set(
              hitPose.transform.position.x,
              hitPose.transform.position.y,
              hitPose.transform.position.z
            );
            this.reticle.quaternion.set(
              hitPose.transform.orientation.x,
              hitPose.transform.orientation.y,
              hitPose.transform.orientation.z,
              hitPose.transform.orientation.w
            );
          }
        } else {
          this.reticle.visible = false;
        }
      }
      
      // Update anchored objects
      for (const anchorId in this.anchors) {
        const anchor = this.anchors[anchorId];
        
        // Update anchor poses
        if (frame.trackedAnchors && frame.trackedAnchors.has(anchor.xrAnchor)) {
          const anchorPose = frame.getPose(anchor.xrAnchor.anchorSpace, referenceSpace);
          
          if (anchorPose) {
            anchor.model.position.set(
              anchorPose.transform.position.x,
              anchorPose.transform.position.y,
              anchorPose.transform.position.z
            );
            anchor.model.quaternion.set(
              anchorPose.transform.orientation.x,
              anchorPose.transform.orientation.y,
              anchorPose.transform.orientation.z,
              anchorPose.transform.orientation.w
            );
          }
        }
      }
    }
    
    // Render the scene
    this.renderer.render(this.scene, this.camera);
  }
  
  /**
   * Preload 3D models
   */
  async preloadModels() {
    // In a real implementation, this would load actual models using GLTFLoader
    // For this example, we'll create placeholder models
    
    this.models.stomach_full = this.createPlaceholderModel('stomach_full');
    this.models.tumor_t1 = this.createPlaceholderModel('tumor_t1');
    this.models.gastrectomy_total = this.createPlaceholderModel('gastrectomy_total');
    this.models.lymph_nodes = this.createPlaceholderModel('lymph_nodes');
    
    console.log('Models preloaded');
  }
  
  /**
   * Create a placeholder model
   * @param {string} modelId - The model ID
   * @returns {THREE.Group} - The model group
   */
  createPlaceholderModel(modelId) {
    const group = new THREE.Group();
    
    let geometry, material;
    
    if (modelId === 'stomach_full') {
      geometry = new THREE.TorusGeometry(0.2, 0.05, 16, 50);
      material = new THREE.MeshStandardMaterial({
        color: 0xf96854,
        metalness: 0.1,
        roughness: 0.5
      });
    } else if (modelId.startsWith('tumor')) {
      geometry = new THREE.SphereGeometry(0.1, 32, 32);
      material = new THREE.MeshStandardMaterial({
        color: 0xff0000,
        metalness: 0.1,
        roughness: 0.5
      });
    } else if (modelId.startsWith('gastrectomy')) {
      geometry = new THREE.CylinderGeometry(0.1, 0.1, 0.2, 32);
      material = new THREE.MeshStandardMaterial({
        color: 0x00aaff,
        metalness: 0.1,
        roughness: 0.5
      });
    } else if (modelId === 'lymph_nodes') {
      // Create multiple small spheres for lymph nodes
      for (let i = 0; i < 15; i++) {
        const nodeGeometry = new THREE.SphereGeometry(0.02, 16, 16);
        const nodeMaterial = new THREE.MeshStandardMaterial({
          color: 0x88ff88,
          metalness: 0.1,
          roughness: 0.5
        });
        
        const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
        node.position.set(
          Math.random() * 0.4 - 0.2,
          Math.random() * 0.4 - 0.2,
          Math.random() * 0.4 - 0.2
        );
        
        group.add(node);
      }
      
      return group;
    } else {
      geometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
      material = new THREE.MeshStandardMaterial({
        color: 0xaaaaaa,
        metalness: 0.1,
        roughness: 0.5
      });
    }
    
    const mesh = new THREE.Mesh(geometry, material);
    group.add(mesh);
    
    // Add labels if enabled
    if (this.options.showLabels) {
      this.addLabelToModel(group, this.getModelNameById(modelId));
    }
    
    return group;
  }
  
  /**
   * Add a text label to a model
   * @param {THREE.Group} modelGroup - The model group
   * @param {string} labelText - The label text
   */
  addLabelToModel(modelGroup, labelText) {
    // In a real implementation, we would use TextGeometry or HTML overlay
    // For this example, we'll create a simple sprite
    
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;
    
    context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    context.font = '24px Arial';
    context.fillStyle = 'white';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(labelText, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(0.3, 0.075, 1);
    sprite.position.y = 0.3;
    
    modelGroup.add(sprite);
  }
  
  /**
   * Place a model in AR space
   */
  async placeModel() {
    if (!this.isInARMode || !this.reticle.visible) return;
    
    try {
      // Get the model to place
      const model = this.models[this.currentModelId];
      if (!model) {
        console.error('Model not found:', this.currentModelId);
        return;
      }
      
      // Clone the model
      const modelInstance = model.clone();
      
      // Position at the reticle
      modelInstance.position.copy(this.reticle.position);
      modelInstance.quaternion.copy(this.reticle.quaternion);
      
      // Add to scene
      this.scene.add(modelInstance);
      
      // Create XR anchor
      if (this.xrSession.createAnchor) {
        const anchor = await this.xrSession.createAnchor(
          new XRRigidTransform(
            { x: this.reticle.position.x, y: this.reticle.position.y, z: this.reticle.position.z },
            { x: this.reticle.quaternion.x, y: this.reticle.quaternion.y, z: this.reticle.quaternion.z, w: this.reticle.quaternion.w }
          ),
          this.xrReferenceSpace
        );
        
        // Store anchor and model
        const anchorId = 'anchor-' + Date.now();
        this.anchors[anchorId] = {
          xrAnchor: anchor,
          model: modelInstance,
          modelId: this.currentModelId,
          timestamp: new Date().toISOString()
        };
        
        // Add interactivity if enabled
        if (this.options.interactiveMode) {
          this.makeModelInteractive(modelInstance, anchorId);
        }
        
        // Trigger haptic feedback if enabled
        if (this.options.enableHapticFeedback && navigator.vibrate) {
          navigator.vibrate(100);
        }
        
        // Log the placement for compliance
        this.logAREvent('model-placed', {
          modelId: this.currentModelId,
          position: {
            x: this.reticle.position.x,
            y: this.reticle.position.y,
            z: this.reticle.position.z
          },
          timestamp: new Date().toISOString()
        });
        
        console.log('Model placed and anchored');
      } else {
        console.warn('Anchors not supported, model will not be anchored');
        
        // Store the model without an anchor
        const modelId = 'model-' + Date.now();
        this.models[modelId] = modelInstance;
      }
    } catch (error) {
      console.error('Failed to place model:', error);
    }
  }
  
  /**
   * Make a model interactive
   * @param {THREE.Group} model - The model to make interactive
   * @param {string} anchorId - The anchor ID
   */
  makeModelInteractive(model, anchorId) {
    // In a real implementation, we would add raycasting for selection
    // and gesture handling for manipulation
    
    // Add a highlight effect to indicate interactivity
    const highlight = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 32, 32),
      new THREE.MeshBasicMaterial({
        color: 0x00aaff,
        transparent: true,
        opacity: 0.3,
        wireframe: true
      })
    );
    
    model.add(highlight);
    
    // Scale animation for visual feedback
    const pulse = () => {
      highlight.scale.x = 1 + 0.1 * Math.sin(Date.now() * 0.003);
      highlight.scale.y = 1 + 0.1 * Math.sin(Date.now() * 0.003);
      highlight.scale.z = 1 + 0.1 * Math.sin(Date.now() * 0.003);
    };
    
    model.userData.animations = model.userData.animations || [];
    model.userData.animations.push(pulse);
    
    // Add to the render loop
    const originalRenderLoop = this.xrRenderLoop.bind(this);
    this.xrRenderLoop = (time, frame) => {
      // Run all model animations
      for (const anchorId in this.anchors) {
        const anchor = this.anchors[anchorId];
        const model = anchor.model;
        
        if (model.userData.animations) {
          model.userData.animations.forEach(animation => animation());
        }
      }
      
      // Call the original render loop
      originalRenderLoop(time, frame);
    };
  }
  
  /**
   * End the AR session
   */
  endARSession() {
    if (this.xrSession) {
      this.xrSession.end();
    }
  }
  
  /**
   * Handle AR session ending
   */
  onARSessionEnded() {
    // Clean up resources
    if (this.xrHitTestSource) {
      this.xrHitTestSource.cancel();
      this.xrHitTestSource = null;
    }
    
    this.xrSession = null;
    this.renderer.setAnimationLoop(null);
    
    // Log session end for compliance
    this.logAREvent('session-ended', {
      timestamp: new Date().toISOString()
    });
    
    console.log('AR session ended');
  }
  
  /**
   * Log an AR event for compliance
   * @param {string} eventType - The event type
   * @param {Object} eventData - The event data
   */
  logAREvent(eventType, eventData) {
    // In a real implementation, this would log to a secure audit service
    
    fetch('/api/audit/ar-event', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        eventType,
        ...eventData,
        userId: this.getUserId()
      })
    }).catch(error => {
      console.error('Failed to log AR event:', error);
    });
  }
  
  /**
   * Get the current user ID
   * @returns {string} - The user ID
   */
  getUserId() {
    // In a real implementation, this would get the user ID from the app context
    return 'user-123';
  }
  
  /**
   * Show an error message
   * @param {string} message - The error message
   */
  showError(message) {
    const errorElement = document.createElement('div');
    errorElement.className = 'gastric-ar-error';
    errorElement.textContent = message;
    
    this.container.appendChild(errorElement);
    
    setTimeout(() => {
      errorElement.remove();
    }, 5000);
  }
  
  /**
   * Take a screenshot of the current AR view
   * @returns {Promise<string>} - A data URL of the screenshot
   */
  takeScreenshot() {
    return new Promise((resolve) => {
      this.renderer.domElement.toBlob(blob => {
        const url = URL.createObjectURL(blob);
        resolve(url);
        
        // Log screenshot for compliance
        this.logAREvent('screenshot-taken', {
          timestamp: new Date().toISOString()
        });
      });
    });
  }
  
  /**
   * Export the current AR scene to the surgical plan
   * @returns {Promise<boolean>} - Whether the export was successful
   */
  async exportToSurgicalPlan() {
    try {
      // Take a screenshot
      const screenshotUrl = await this.takeScreenshot();
      
      // Collect model placements
      const placements = Object.values(this.anchors).map(anchor => ({
        modelId: anchor.modelId,
        position: {
          x: anchor.model.position.x,
          y: anchor.model.position.y,
          z: anchor.model.position.z
        },
        rotation: {
          x: anchor.model.quaternion.x,
          y: anchor.model.quaternion.y,
          z: anchor.model.quaternion.z,
          w: anchor.model.quaternion.w
        },
        timestamp: anchor.timestamp
      }));
      
      // Create plan data
      const planData = {
        screenshot: screenshotUrl,
        placements,
        timestamp: new Date().toISOString(),
        userId: this.getUserId()
      };
      
      // Send to the API
      const response = await fetch('/api/surgical-plan/ar-visualization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(planData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      // Log export for compliance
      this.logAREvent('exported-to-plan', {
        timestamp: new Date().toISOString()
      });
      
      return true;
    } catch (error) {
      console.error('Failed to export to surgical plan:', error);
      this.showError('Failed to export: ' + error.message);
      return false;
    }
  }
  
  /**
   * Clean up resources
   */
  dispose() {
    // End AR session if active
    if (this.isInARMode) {
      this.endARSession();
    }
    
    // Clean up Three.js resources
    if (this.renderer) {
      this.renderer.dispose();
    }
    
    // Clear the container
    if (this.container) {
      this.container.innerHTML = '';
    }
    
    console.log('AR visualization disposed');
  }
}

// Export the class
window.GastricARVisualization = GastricARVisualization;
