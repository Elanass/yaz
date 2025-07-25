/**
 * AI Analytics Worker for Gastric ADCI Platform
 * Performs computation-intensive analytics tasks in a separate thread
 * 
 * This worker handles:
 * - Loading and running TensorFlow.js models
 * - Statistical analysis of patient data
 * - Predictive modeling for clinical outcomes
 * - Confidence interval calculations
 */

// Import TensorFlow.js (when running in a real environment)
// importScripts('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.2.0/dist/tf.min.js');

// Cache for loaded models
const modelCache = new Map();

// Current task being processed
let currentTask = null;

// Listen for messages from the main thread
self.addEventListener('message', async (event) => {
    const data = event.data;
    
    try {
        switch (data.action) {
            case 'loadModel':
                await loadModel(data.modelId, data.modelInfo);
                break;
                
            case 'runAnalysis':
                await runAnalysis(data.taskId, data.analysisType, data.patientData, 
                                data.cohortData, data.options, data.modelId);
                break;
                
            case 'cancelAnalysis':
                cancelCurrentAnalysis(data.taskId);
                break;
                
            default:
                throw new Error(`Unknown action: ${data.action}`);
        }
    } catch (error) {
        handleError(data, error);
    }
});

/**
 * Load a machine learning model
 * @param {string} modelId - The ID of the model to load
 * @param {Object} modelInfo - Information about the model
 */
async function loadModel(modelId, modelInfo) {
    try {
        // Check if model is already loaded
        if (modelCache.has(modelId)) {
            self.postMessage({
                action: 'modelLoaded',
                modelId: modelId
            });
            return;
        }
        
        // For demonstration in this mock implementation, we're simulating model loading
        // In a real implementation, we would use TensorFlow.js to load the actual model
        
        // Simulate network delay and model initialization
        await simulateModelLoading(modelInfo);
        
        // Cache the "model" (in real implementation, this would be a tf.LayersModel or similar)
        modelCache.set(modelId, {
            id: modelId,
            info: modelInfo,
            // In real implementation: model: loadedModel,
            loadTime: Date.now()
        });
        
        // Notify main thread that model is loaded
        self.postMessage({
            action: 'modelLoaded',
            modelId: modelId
        });
    } catch (error) {
        self.postMessage({
            action: 'modelLoadError',
            modelId: modelId,
            error: error.message
        });
    }
}

/**
 * Simulate model loading with realistic delays
 * In a real implementation, this would be replaced with actual model loading code
 */
async function simulateModelLoading(modelInfo) {
    // Simulate loading time based on model size
    const size = modelInfo.size || 'medium';
    let loadTime = 1000; // Default 1 second
    
    switch (size) {
        case 'tiny':
            loadTime = 500;
            break;
        case 'small':
            loadTime = 1000;
            break;
        case 'compact':
            loadTime = 2000;
            break;
        case 'medium':
            loadTime = 3000;
            break;
        case 'large':
            loadTime = 5000;
            break;
        case 'xlarge':
            loadTime = 8000;
            break;
    }
    
    // Simulate progress updates
    for (let progress = 0; progress <= 100; progress += 10) {
        // In real implementation, we would report actual loading progress
        await new Promise(resolve => setTimeout(resolve, loadTime / 10));
    }
}

/**
 * Run an analysis task with the specified model
 * @param {string} taskId - The ID of the analysis task
 * @param {string} analysisType - The type of analysis to run
 * @param {Object} patientData - Patient data for individual analysis
 * @param {Array} cohortData - Cohort data for population analysis
 * @param {Object} options - Analysis options
 * @param {string} modelId - The ID of the model to use
 */
async function runAnalysis(taskId, analysisType, patientData, cohortData, options, modelId) {
    // Set current task
    currentTask = {
        id: taskId,
        cancelled: false
    };
    
    try {
        // Validate required data
        if (!analysisType) {
            throw new Error('Analysis type is required');
        }
        
        if (analysisType !== 'cohort-analysis' && !patientData) {
            throw new Error('Patient data is required for this analysis type');
        }
        
        if (analysisType === 'cohort-analysis' && (!cohortData || !Array.isArray(cohortData))) {
            throw new Error('Valid cohort data array is required for cohort analysis');
        }
        
        // Check if we need a model for this analysis
        if (modelId && !modelCache.has(modelId)) {
            throw new Error(`Model ${modelId} not loaded. Please load the model first.`);
        }
        
        // Update progress to indicate we're starting
        updateProgress(taskId, 10);
        
        // Prepare data for analysis
        const preparedData = await prepareDataForAnalysis(
            analysisType, 
            patientData, 
            cohortData, 
            options
        );
        
        // Check if task was cancelled during data preparation
        if (currentTask.cancelled) {
            return;
        }
        
        updateProgress(taskId, 30);
        
        // Run the appropriate analysis based on type
        let result;
        switch (analysisType) {
            case 'recurrence-prediction':
                result = await runRecurrencePrediction(preparedData, modelId, options);
                break;
                
            case 'complication-risk':
                result = await runComplicationRiskAnalysis(preparedData, modelId, options);
                break;
                
            case 'length-of-stay':
                result = await runLengthOfStayPrediction(preparedData, modelId, options);
                break;
                
            case 'readmission-risk':
                result = await runReadmissionRiskAnalysis(preparedData, modelId, options);
                break;
                
            case 'treatment-response':
                result = await runTreatmentResponseAnalysis(preparedData, modelId, options);
                break;
                
            case 'survival-analysis':
                result = await runSurvivalAnalysis(preparedData, modelId, options);
                break;
                
            case 'protocol-compliance':
                result = await runProtocolComplianceAnalysis(preparedData, modelId, options);
                break;
                
            case 'cohort-analysis':
                result = await runCohortAnalysis(preparedData, options);
                break;
                
            default:
                throw new Error(`Unsupported analysis type: ${analysisType}`);
        }
        
        // Check if task was cancelled during analysis
        if (currentTask.cancelled) {
            return;
        }
        
        updateProgress(taskId, 90);
        
        // Add confidence intervals and uncertainty metrics
        result = addConfidenceMetrics(result, analysisType);
        
        // Send results back to main thread
        self.postMessage({
            action: 'analysisResult',
            taskId: taskId,
            result: result
        });
        
        // Clear current task
        currentTask = null;
    } catch (error) {
        // Handle errors
        self.postMessage({
            action: 'analysisError',
            taskId: taskId,
            error: error.message
        });
        
        // Clear current task
        currentTask = null;
    }
}

/**
 * Cancel the current analysis task if it matches the given task ID
 */
function cancelCurrentAnalysis(taskId) {
    if (currentTask && currentTask.id === taskId) {
        currentTask.cancelled = true;
    }
}

/**
 * Update the progress of the current analysis task
 */
function updateProgress(taskId, progress) {
    self.postMessage({
        action: 'analysisProgress',
        taskId: taskId,
        progress: progress
    });
}

/**
 * Handle errors from any operation
 */
function handleError(data, error) {
    console.error('Worker error:', error);
    
    if (data.action === 'loadModel') {
        self.postMessage({
            action: 'modelLoadError',
            modelId: data.modelId,
            error: error.message
        });
    } else if (data.action === 'runAnalysis') {
        self.postMessage({
            action: 'analysisError',
            taskId: data.taskId,
            error: error.message
        });
    } else {
        self.postMessage({
            action: 'error',
            error: error.message
        });
    }
}

/**
 * Prepare data for analysis by cleaning, normalizing, and formatting
 */
async function prepareDataForAnalysis(analysisType, patientData, cohortData, options) {
    // This would contain data preprocessing logic specific to each analysis type
    // For this mock implementation, we'll just return the data as-is with simulated delay
    
    // Simulate data preparation time
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (analysisType === 'cohort-analysis') {
        return cohortData;
    } else {
        return patientData;
    }
}

/**
 * Run recurrence prediction analysis
 */
async function runRecurrencePrediction(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock result with appropriate clinical parameters
    return {
        recurrenceProbability: 0.27,
        timeToRecurrenceMonths: {
            median: 24,
            range: [18, 36]
        },
        riskFactors: [
            { factor: 'Tumor Stage', contribution: 0.35, value: patientData.tumorStaging?.stage || 'Unknown' },
            { factor: 'Margin Status', contribution: 0.25, value: patientData.surgicalDetails?.marginStatus || 'Unknown' },
            { factor: 'Lymph Node Involvement', contribution: 0.20, value: patientData.tumorStaging?.nodesPositive || 'Unknown' },
            { factor: 'Histological Grade', contribution: 0.15, value: patientData.tumorStaging?.grade || 'Unknown' },
            { factor: 'Age', contribution: 0.05, value: patientData.demographics?.age || 'Unknown' }
        ],
        recommendations: [
            { text: 'Consider more frequent follow-up imaging in first 18 months', confidence: 0.85 },
            { text: 'Monitor tumor markers every 3 months for first 2 years', confidence: 0.78 }
        ],
        supportingEvidence: [
            { citation: 'Smith et al. (2022). Recurrence patterns in gastric cancer. J Surg Oncol.', relevance: 0.9 },
            { citation: 'Johnson et al. (2021). Predictors of early recurrence after gastrectomy. Ann Surg.', relevance: 0.85 }
        ]
    };
}

/**
 * Run complication risk analysis
 */
async function runComplicationRiskAnalysis(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 1200));
    
    // Mock result with appropriate clinical parameters
    return {
        overallComplicationRisk: 0.32,
        specificRisks: [
            { complication: 'Anastomotic Leak', probability: 0.09, timeframe: '7-10 days post-op' },
            { complication: 'Surgical Site Infection', probability: 0.15, timeframe: '5-14 days post-op' },
            { complication: 'Pneumonia', probability: 0.12, timeframe: '3-7 days post-op' },
            { complication: 'VTE', probability: 0.08, timeframe: '1-4 weeks post-op' },
            { complication: 'Ileus', probability: 0.14, timeframe: '2-5 days post-op' }
        ],
        preventiveStrategies: [
            { strategy: 'Enhanced Recovery After Surgery (ERAS) Protocol', effectiveness: 0.65 },
            { strategy: 'Early Ambulation', effectiveness: 0.55 },
            { strategy: 'Prophylactic Antibiotics', effectiveness: 0.75 },
            { strategy: 'VTE Prophylaxis', effectiveness: 0.80 },
            { strategy: 'Nutritional Optimization', effectiveness: 0.60 }
        ],
        patientSpecificFactors: [
            { factor: 'BMI', impact: 'moderate', value: patientData.demographics?.bmi || 'Unknown' },
            { factor: 'Smoking Status', impact: 'high', value: patientData.demographics?.smokingStatus || 'Unknown' },
            { factor: 'Diabetes', impact: 'moderate', value: patientData.medicalHistory?.diabetes || 'Unknown' },
            { factor: 'Prior Abdominal Surgery', impact: 'low', value: patientData.surgicalHistory?.priorAbdominalSurgery || 'Unknown' }
        ]
    };
}

/**
 * Run length of stay prediction
 */
async function runLengthOfStayPrediction(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock result with appropriate clinical parameters
    return {
        predictedLOS: {
            mean: 8.5,
            median: 7,
            range: [6, 12]
        },
        factorsAffectingLOS: [
            { factor: 'Age', impact: 0.25, value: patientData.demographics?.age || 'Unknown' },
            { factor: 'Comorbidity Count', impact: 0.30, value: patientData.medicalHistory?.comorbidityCount || 'Unknown' },
            { factor: 'Surgical Approach', impact: 0.20, value: patientData.surgicalDetails?.approach || 'Unknown' },
            { factor: 'Extent of Resection', impact: 0.15, value: patientData.surgicalDetails?.resectionExtent || 'Unknown' },
            { factor: 'ERAS Protocol Compliance', impact: 0.10, value: patientData.perioperativeCare?.erasCompliance || 'Unknown' }
        ],
        dischargePlanning: {
            readiness: [
                { milestone: 'Return of Bowel Function', estimatedDay: 3 },
                { milestone: 'Adequate Pain Control with Oral Meds', estimatedDay: 4 },
                { milestone: 'Independent Ambulation', estimatedDay: 2 },
                { milestone: 'Tolerating Oral Diet', estimatedDay: 5 }
            ],
            recommendedSupport: [
                { support: 'Home Health Nursing', indicated: true },
                { support: 'Physical Therapy', indicated: false },
                { support: 'Nutritional Support', indicated: true }
            ]
        }
    };
}

/**
 * Run readmission risk analysis
 */
async function runReadmissionRiskAnalysis(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 1100));
    
    // Mock result with appropriate clinical parameters
    return {
        readmissionRisk30Day: 0.18,
        readmissionRisk90Day: 0.24,
        riskFactors: [
            { factor: 'Comorbidity Index', contribution: 0.30, value: patientData.medicalHistory?.comorbidityIndex || 'Unknown' },
            { factor: 'Length of Initial Stay', contribution: 0.20, value: patientData.hospitalCourse?.lengthOfStay || 'Unknown' },
            { factor: 'Discharge Disposition', contribution: 0.15, value: patientData.hospitalCourse?.dischargeDisposition || 'Unknown' },
            { factor: 'Perioperative Complications', contribution: 0.25, value: patientData.hospitalCourse?.complications || 'Unknown' },
            { factor: 'Social Support', contribution: 0.10, value: patientData.socialHistory?.support || 'Unknown' }
        ],
        commonReadmissionCauses: [
            { cause: 'Surgical Site Infection', probability: 0.25 },
            { cause: 'Dehydration/Malnutrition', probability: 0.20 },
            { cause: 'Abdominal Pain/Ileus', probability: 0.18 },
            { cause: 'Anastomotic Leak', probability: 0.10 },
            { cause: 'Medication Issues', probability: 0.15 }
        ],
        preventiveRecommendations: [
            { recommendation: 'Structured Follow-up Phone Call at 48-72 Hours', strength: 'Strong' },
            { recommendation: 'Early Post-discharge Office Visit (5-7 Days)', strength: 'Strong' },
            { recommendation: 'Detailed Medication Reconciliation', strength: 'Moderate' },
            { recommendation: 'Nutrition Consultation Prior to Discharge', strength: 'Moderate' }
        ]
    };
}

/**
 * Run treatment response analysis
 */
async function runTreatmentResponseAnalysis(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 1300));
    
    // Mock result with appropriate clinical parameters
    return {
        predictedResponse: {
            category: 'Partial Response',
            probability: 0.68,
            timeframe: '3-6 months'
        },
        responseByTreatmentType: [
            { treatment: 'FLOT Chemotherapy', responseProbability: 0.72, confidenceInterval: [0.65, 0.79] },
            { treatment: 'Standard Gastrectomy', responseProbability: 0.85, confidenceInterval: [0.78, 0.91] },
            { treatment: 'Adjuvant Chemoradiation', responseProbability: 0.64, confidenceInterval: [0.57, 0.71] }
        ],
        biomarkers: [
            { marker: 'HER2 Status', predictiveValue: 'High', value: patientData.biomarkers?.her2Status || 'Unknown' },
            { marker: 'PD-L1 Expression', predictiveValue: 'Moderate', value: patientData.biomarkers?.pdl1Expression || 'Unknown' },
            { marker: 'Microsatellite Instability', predictiveValue: 'High', value: patientData.biomarkers?.msiStatus || 'Unknown' },
            { marker: 'Tumor Mutation Burden', predictiveValue: 'Moderate', value: patientData.biomarkers?.tmb || 'Unknown' }
        ],
        potentialAdverseEffects: [
            { effect: 'Neutropenia', probability: 0.40, severity: 'Moderate', management: 'Dose reduction, G-CSF support' },
            { effect: 'Nausea/Vomiting', probability: 0.55, severity: 'Mild to Moderate', management: 'Antiemetic protocol' },
            { effect: 'Fatigue', probability: 0.70, severity: 'Mild to Moderate', management: 'Activity pacing, nutritional support' },
            { effect: 'Peripheral Neuropathy', probability: 0.30, severity: 'Mild', management: 'Dose modification, gabapentin' }
        ]
    };
}

/**
 * Run survival analysis
 */
async function runSurvivalAnalysis(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock result with appropriate clinical parameters
    return {
        overallSurvival: {
            median: 36.4, // months
            confidenceInterval: [28.6, 42.3],
            survivalProbabilities: [
                { timepoint: '1-year', probability: 0.82, confidenceInterval: [0.77, 0.87] },
                { timepoint: '3-year', probability: 0.51, confidenceInterval: [0.44, 0.58] },
                { timepoint: '5-year', probability: 0.33, confidenceInterval: [0.26, 0.40] }
            ]
        },
        diseaseFreeSurvival: {
            median: 24.8, // months
            confidenceInterval: [19.5, 30.1],
            survivalProbabilities: [
                { timepoint: '1-year', probability: 0.74, confidenceInterval: [0.68, 0.80] },
                { timepoint: '3-year', probability: 0.38, confidenceInterval: [0.31, 0.45] },
                { timepoint: '5-year', probability: 0.25, confidenceInterval: [0.19, 0.31] }
            ]
        },
        prognosticFactors: [
            { factor: 'TNM Stage', hazardRatio: 2.4, pValue: 0.001, value: patientData.tumorStaging?.tnmStage || 'Unknown' },
            { factor: 'R0 Resection', hazardRatio: 0.65, pValue: 0.003, value: patientData.surgicalDetails?.resectionStatus || 'Unknown' },
            { factor: 'Lymphovascular Invasion', hazardRatio: 1.7, pValue: 0.02, value: patientData.pathology?.lymphovascularInvasion || 'Unknown' },
            { factor: 'Signet Ring Histology', hazardRatio: 1.9, pValue: 0.01, value: patientData.pathology?.histology || 'Unknown' },
            { factor: 'Adjuvant Therapy Completion', hazardRatio: 0.72, pValue: 0.008, value: patientData.treatmentHistory?.adjuvantCompletion || 'Unknown' }
        ],
        comparisons: {
            description: 'Comparison to similar patients in database',
            survivalDifference: -0.08, // negative means worse than cohort
            pValue: 0.12
        }
    };
}

/**
 * Run protocol compliance analysis
 */
async function runProtocolComplianceAnalysis(patientData, modelId, options) {
    // Simulate model inference
    await new Promise(resolve => setTimeout(resolve, 900));
    
    // Mock result with appropriate clinical parameters
    return {
        overallCompliance: 0.78, // 78% compliant with protocol
        complianceByCategory: [
            { category: 'Preoperative Assessment', compliance: 0.92, impact: 'High' },
            { category: 'Nutritional Optimization', compliance: 0.85, impact: 'High' },
            { category: 'Intraoperative Management', compliance: 0.88, impact: 'High' },
            { category: 'Pain Management', compliance: 0.76, impact: 'Moderate' },
            { category: 'Early Mobilization', compliance: 0.81, impact: 'High' },
            { category: 'Fluid Management', compliance: 0.72, impact: 'Moderate' },
            { category: 'Drain Management', compliance: 0.64, impact: 'Moderate' }
        ],
        deviations: [
            { protocol: 'Early Oral Feeding', deviation: 'Delayed by 24 hours', reason: 'Postop ileus', impact: 'Moderate' },
            { protocol: 'Urinary Catheter Removal', deviation: 'Retained 48h longer than protocol', reason: 'Patient mobility issues', impact: 'Low' },
            { protocol: 'Multimodal Analgesia', deviation: 'Incomplete implementation', reason: 'Patient allergy to NSAID', impact: 'Moderate' }
        ],
        outcomesCorrelation: [
            { outcome: 'Length of Stay', correlation: -0.65, pValue: 0.001 }, // Negative correlation (higher compliance = shorter stay)
            { outcome: 'Complication Rate', correlation: -0.58, pValue: 0.003 },
            { outcome: 'Readmission Rate', correlation: -0.42, pValue: 0.02 },
            { outcome: 'Patient Satisfaction', correlation: 0.71, pValue: 0.001 }
        ],
        recommendations: [
            { area: 'Drain Management', recommendation: 'Implement standardized criteria for drain removal', priority: 'High' },
            { area: 'Pain Management', recommendation: 'Develop alternative protocol for NSAID-allergic patients', priority: 'Medium' },
            { area: 'Early Mobilization', recommendation: 'Consult PT for patients with mobility limitations', priority: 'Medium' }
        ]
    };
}

/**
 * Run cohort analysis
 */
async function runCohortAnalysis(cohortData, options) {
    // Simulate analysis time
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock result with appropriate clinical parameters
    return {
        cohortSize: cohortData.length,
        demographics: {
            ageDistribution: {
                mean: 64.5,
                median: 65,
                range: [32, 89],
                distribution: [
                    { range: '30-39', count: 15, percentage: 0.03 },
                    { range: '40-49', count: 45, percentage: 0.09 },
                    { range: '50-59', count: 120, percentage: 0.24 },
                    { range: '60-69', count: 170, percentage: 0.34 },
                    { range: '70-79', count: 105, percentage: 0.21 },
                    { range: '80+', count: 45, percentage: 0.09 }
                ]
            },
            genderDistribution: [
                { gender: 'Male', count: 305, percentage: 0.61 },
                { gender: 'Female', count: 195, percentage: 0.39 }
            ],
            comorbidities: [
                { condition: 'Hypertension', count: 225, percentage: 0.45 },
                { condition: 'Diabetes', count: 150, percentage: 0.30 },
                { condition: 'Coronary Artery Disease', count: 100, percentage: 0.20 },
                { condition: 'COPD', count: 75, percentage: 0.15 },
                { condition: 'Chronic Kidney Disease', count: 60, percentage: 0.12 }
            ]
        },
        diseaseCharacteristics: {
            stageDistribution: [
                { stage: 'Stage I', count: 100, percentage: 0.20 },
                { stage: 'Stage II', count: 150, percentage: 0.30 },
                { stage: 'Stage III', count: 200, percentage: 0.40 },
                { stage: 'Stage IV', count: 50, percentage: 0.10 }
            ],
            histologyDistribution: [
                { type: 'Intestinal', count: 250, percentage: 0.50 },
                { type: 'Diffuse', count: 150, percentage: 0.30 },
                { type: 'Mixed', count: 75, percentage: 0.15 },
                { type: 'Other', count: 25, percentage: 0.05 }
            ],
            biomarkerDistribution: [
                { marker: 'HER2+', count: 85, percentage: 0.17 },
                { marker: 'MSI-High', count: 45, percentage: 0.09 },
                { marker: 'PD-L1 High', count: 95, percentage: 0.19 }
            ]
        },
        treatmentPatterns: {
            surgicalApproaches: [
                { approach: 'Open Gastrectomy', count: 225, percentage: 0.45 },
                { approach: 'Laparoscopic Gastrectomy', count: 200, percentage: 0.40 },
                { approach: 'Robotic Gastrectomy', count: 75, percentage: 0.15 }
            ],
            neoadjuvantTherapy: [
                { therapy: 'FLOT', count: 180, percentage: 0.36 },
                { therapy: 'Other Chemotherapy', count: 100, percentage: 0.20 },
                { therapy: 'None', count: 220, percentage: 0.44 }
            ],
            adjuvantTherapy: [
                { therapy: 'Chemotherapy', count: 275, percentage: 0.55 },
                { therapy: 'Chemoradiation', count: 100, percentage: 0.20 },
                { therapy: 'None', count: 125, percentage: 0.25 }
            ]
        },
        outcomes: {
            overallSurvival: {
                median: 32.6, // months
                rates: [
                    { timepoint: '1-year', rate: 0.80 },
                    { timepoint: '3-year', rate: 0.48 },
                    { timepoint: '5-year', rate: 0.31 }
                ]
            },
            recurrencePatterns: [
                { pattern: 'Local', count: 65, percentage: 0.13 },
                { pattern: 'Regional', count: 85, percentage: 0.17 },
                { pattern: 'Distant', count: 150, percentage: 0.30 },
                { pattern: 'No Recurrence', count: 200, percentage: 0.40 }
            ],
            complicationRates: [
                { complication: 'Anastomotic Leak', count: 40, percentage: 0.08 },
                { complication: 'Surgical Site Infection', count: 75, percentage: 0.15 },
                { complication: 'Pneumonia', count: 60, percentage: 0.12 },
                { complication: 'VTE', count: 35, percentage: 0.07 }
            ],
            lengthOfStay: {
                mean: 9.2,
                median: 8.0,
                range: [4, 28]
            },
            readmissions: {
                rate30Day: 0.16,
                rate90Day: 0.22
            }
        },
        comparisons: {
            description: 'Comparison to national gastric cancer registry data',
            survivalDifference: 0.04, // positive means better than registry
            complicationDifference: -0.03, // negative means fewer complications
            readmissionDifference: -0.02 // negative means fewer readmissions
        }
    };
}

/**
 * Add confidence intervals and uncertainty metrics to results
 */
function addConfidenceMetrics(result, analysisType) {
    // For this mock implementation, we'll just add some predefined confidence metrics
    // In a real implementation, these would be calculated based on model output
    
    // Add general confidence metrics
    result.confidenceMetrics = {
        modelConfidence: 0.85, // Overall model confidence
        dataCompleteness: 0.92, // Completeness of input data
        predictionInterval: 0.12, // Width of prediction interval
        uncertaintySources: [
            { source: 'Model Limitations', impact: 'Moderate' },
            { source: 'Data Quality', impact: 'Low' },
            { source: 'Patient-Specific Factors', impact: 'Moderate' }
        ]
    };
    
    // Add analysis-specific confidence metrics
    switch (analysisType) {
        case 'recurrence-prediction':
            result.confidenceMetrics.specificMetrics = {
                calibrationScore: 0.88,
                discriminationAUC: 0.76,
                sensitivityAtSpecificThreshold: 0.82
            };
            break;
            
        case 'survival-analysis':
            result.confidenceMetrics.specificMetrics = {
                concordanceIndex: 0.72,
                bootstrapValidation: 0.68,
                calibrationSlope: 0.91
            };
            break;
    }
    
    return result;
}
